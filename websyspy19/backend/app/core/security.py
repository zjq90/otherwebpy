"""
安全模块
处理密码加密、JWT令牌生成和验�?
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# 密码上下文，用于加密和验证密�?
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    参数:
        plain_password: 明文密码
        hashed_password: 哈希密码
    
    返回:
        验证成功返回True，否则返回False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码的哈希�?
    
    参数:
        password: 明文密码
    
    返回:
        哈希后的密码字符�?
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    参数:
        subject: 令牌主题，通常是用户ID
        expires_delta: 过期时间增量，如果为None则使用默认�?
    
    返回:
        JWT令牌字符�?
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 构建JWT载荷
    to_encode = {"exp": expire, "sub": str(subject)}
    # 生成JWT令牌
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌
    
    参数:
        token: JWT令牌字符�?
    
    返回:
        解码后的载荷字典，如果验证失败则返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        # 令牌无效或已过期
        return None
