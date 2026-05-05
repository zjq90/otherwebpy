"""
安全工具模块
提供密码哈希、JWT令牌生成和验证等安全功能
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import TokenData

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    :param plain_password: 明文密码
    :param hashed_password: 哈希密码
    :return: 是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    :param password: 明文密码
    :return: 哈希密码
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    :param data: 令牌数据
    :param expires_delta: 过期时间
    :return: JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    用于依赖注入，验证JWT令牌并返回用户信息
    :param token: JWT令牌
    :param db: 数据库会话
    :return: 用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解析JWT令牌
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if user_id is None or username is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id, username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    # 检查用户是否被删除或禁用
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


def require_role(allowed_roles: list[UserRole]):
    """
    角色权限装饰器
    用于限制只有特定角色的用户可以访问某个接口
    :param allowed_roles: 允许的角色列表
    :return: 依赖函数
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要角色: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    
    return role_checker


# 预定义常用的角色检查器
require_admin = require_role([UserRole.ADMIN])
require_dispatcher = require_role([UserRole.ADMIN, UserRole.DISPATCHER])
require_driver = require_role([UserRole.ADMIN, UserRole.DISPATCHER, UserRole.DRIVER])
require_authenticated = require_role([UserRole.ADMIN, UserRole.DISPATCHER, UserRole.DRIVER])
