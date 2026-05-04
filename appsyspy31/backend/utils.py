"""
工具函数模块
包含密码加密、JWT认证、分页等通用工具函数
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel

from config import settings
from database import get_db
from models import User

# ========================================
# 密码加密相关
# ========================================

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    生成密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

# ========================================
# JWT认证相关
# ========================================

class TokenData(BaseModel):
    """JWT令牌中存储的数据"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 过期时间增量，如果为None则使用默认配置
        
    Returns:
        str: JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """
    解码JWT访问令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        Optional[TokenData]: 解码后的令牌数据，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")
        role: str = payload.get("role")
        
        if user_id is None or username is None:
            return None
        
        return TokenData(user_id=user_id, username=username, role=role)
    except JWTError:
        return None

# ========================================
# 用户认证依赖
# ========================================

# 定义HTTP Bearer认证方案
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户的依赖函数
    
    用于需要认证的API端点，从请求头中提取JWT令牌并验证用户身份
    
    Args:
        credentials: HTTP授权凭证
        db: 数据库会话
        
    Returns:
        User: 认证的用户对象
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(credentials.credentials)
    
    if token_data is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户的依赖函数
    
    验证用户是否处于激活状态
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        User: 活跃的用户对象
        
    Raises:
        HTTPException: 用户未激活时抛出400错误
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")
    return current_user

def require_role(*allowed_roles):
    """
    角色权限检查装饰器工厂
    
    创建一个依赖函数，检查当前用户是否具有指定的角色
    
    Args:
        *allowed_roles: 允许的角色列表
        
    Returns:
        依赖函数，用于FastAPI的Depends
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker

# ========================================
# 分页工具
# ========================================

class PaginatedResult(BaseModel):
    """分页查询结果"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

def paginate_query(
    query,
    page: int = 1,
    page_size: int = 10
) -> PaginatedResult:
    """
    对查询结果进行分页处理
    
    Args:
        query: SQLAlchemy查询对象
        page: 当前页码（从1开始）
        page_size: 每页数量
        
    Returns:
        PaginatedResult: 分页结果
    """
    # 计算总记录数
    total = query.count()
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size
    
    # 确保页码在有效范围内
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 执行分页查询
    items = query.offset(offset).limit(page_size).all()
    
    return PaginatedResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

# ========================================
# 通用工具函数
# ========================================

def generate_random_string(length: int = 8) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        str: 随机字符串
    """
    import random
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    格式化datetime对象为字符串
    
    Args:
        dt: datetime对象
        
    Returns:
        Optional[str]: 格式化后的字符串（如：2024-01-15 10:30:00）
    """
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_date(dt: Optional[datetime]) -> Optional[str]:
    """
    格式化datetime对象为日期字符串
    
    Args:
        dt: datetime对象
        
    Returns:
        Optional[str]: 格式化后的日期字符串（如：2024-01-15）
    """
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")

def parse_time_str(time_str: str) -> Optional[datetime]:
    """
    解析时间字符串为datetime对象
    
    Args:
        time_str: 时间字符串（如：09:00）
        
    Returns:
        Optional[datetime]: 解析后的datetime对象
    """
    try:
        return datetime.strptime(time_str, "%H:%M")
    except ValueError:
        return None

def calculate_age(birth_date: Optional[datetime]) -> Optional[int]:
    """
    根据出生日期计算年龄
    
    Args:
        birth_date: 出生日期
        
    Returns:
        Optional[int]: 年龄
    """
    if birth_date is None:
        return None
    
    today = datetime.today()
    age = today.year - birth_date.year
    
    # 检查是否过了今年的生日
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age
