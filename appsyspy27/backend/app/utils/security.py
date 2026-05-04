"""
安全工具模块
包含密码加密、JWT令牌生成和验证等功能
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
security = HTTPBearer()

# bcrypt最大支持72字节
BCRYPT_MAX_BYTES = 72


def _truncate_password_for_bcrypt(password: str) -> str:
    """
    截断密码以符合bcrypt的72字节限制
    
    bcrypt算法有72字节的限制，超过部分会被忽略。
    此函数确保加密和验证时使用相同的截断逻辑。
    
    Args:
        password: 原始密码字符串
        
    Returns:
        str: 截断后的密码字符串
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        return password_bytes[:BCRYPT_MAX_BYTES].decode('utf-8', errors='ignore')
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    plain_password = _truncate_password_for_bcrypt(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    bcrypt有72字节的限制，需要提前截断过长的密码
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    password = _truncate_password_for_bcrypt(password)
    return pwd_context.hash(password)


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        subject: 令牌主题（通常是用户ID）
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        Optional[TokenPayload]: 令牌载荷，如果无效返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        exp: int = payload.get("exp")
        
        if user_id is None:
            return None
        
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return None
        
        expire_time = datetime.fromtimestamp(exp) if exp else None
        
        return TokenPayload(sub=user_id, exp=expire_time)
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（依赖注入函数）
    
    Args:
        credentials: HTTP认证凭证
        db: 数据库会话
        
    Returns:
        User: 当前登录用户对象
        
    Raises:
        HTTPException: 认证失败时抛出
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None or payload.sub is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == payload.sub).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（确保用户已激活）
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前活跃用户
    """
    return current_user
