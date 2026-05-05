"""
安全工具模块
包含密码加密、JWT令牌生成和验证、权限检查等功能
"""

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from ..config import settings
from ..database import get_db
from ..models.user_models import User, Role, Permission


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()


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
    :return: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码令牌
    :param token: JWT令牌
    :return: 令牌数据
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_verification_code() -> str:
    """
    生成6位数字验证码
    :return: 验证码
    """
    import random
    return str(random.randint(100000, 999999))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    :param credentials: 认证凭证
    :param db: 数据库会话
    :return: 用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # 查询用户及角色权限
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


def get_user_permissions(user: User) -> List[str]:
    """
    获取用户的所有权限代码
    :param user: 用户对象
    :return: 权限代码列表
    """
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.code)
    return list(permissions)


def has_permission(user: User, permission_code: str) -> bool:
    """
    检查用户是否拥有指定权限
    :param user: 用户对象
    :param permission_code: 权限代码
    :return: 是否拥有权限
    """
    permissions = get_user_permissions(user)
    return permission_code in permissions


def has_role(user: User, role_code: str) -> bool:
    """
    检查用户是否拥有指定角色
    :param user: 用户对象
    :param role_code: 角色代码
    :return: 是否拥有角色
    """
    for role in user.roles:
        if role.code == role_code:
            return True
    return False


def is_admin(user: User) -> bool:
    """
    检查用户是否是管理员
    :param user: 用户对象
    :return: 是否是管理员
    """
    return has_role(user, "admin")


def require_permission(permission_code: str):
    """
    权限检查依赖装饰器工厂
    :param permission_code: 需要的权限代码
    :return: 依赖函数
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not has_permission(current_user, permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return permission_checker


def require_role(role_code: str):
    """
    角色检查依赖装饰器工厂
    :param role_code: 需要的角色代码
    :return: 依赖函数
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not has_role(current_user, role_code) and not is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker
