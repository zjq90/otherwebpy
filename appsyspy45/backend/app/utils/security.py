"""
安全工具模块
包含密码加密、JWT令牌生成和验证等功能
"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import get_settings

# 获取配置
settings = get_settings()

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    :param subject: 令牌主题（通常是用户ID）
    :param expires_delta: 过期时间增量
    :return: JWT令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Any) -> str:
    """
    创建刷新令牌
    :param subject: 令牌主题
    :return: 刷新令牌
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码JWT令牌
    :param token: JWT令牌
    :return: 解码后的payload，无效则返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    从令牌中获取用户ID
    :param token: JWT令牌
    :return: 用户ID，无效则返回None
    """
    payload = decode_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    return None


def generate_sms_code(length: int = 6) -> str:
    """
    生成短信验证码
    :param length: 验证码长度
    :return: 验证码字符串
    """
    import random
    import string
    return ''.join(random.choices(string.digits, k=length))


def generate_invite_code(length: int = 6) -> str:
    """
    生成邀请码
    :param length: 邀请码长度
    :return: 邀请码字符串
    """
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_order_no(prefix: str = "RC") -> str:
    """
    生成订单号
    格式：前缀 + 时间戳 + 6位随机数
    :param prefix: 订单前缀
    :return: 订单号
    """
    import time
    import random
    timestamp = str(int(time.time()))
    random_num = ''.join(random.choices('0123456789', k=6))
    return f"{prefix}{timestamp}{random_num}"
