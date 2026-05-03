"""
安全工具函数
包含密码加密、JWT令牌生成等功能
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# bcrypt密码长度限制（72字节）
BCRYPT_MAX_LENGTH = 72


def _preprocess_password(password: str) -> str:
    """
    预处理密码以符合bcrypt的72字节限制
    
    bcrypt算法有一个固有限制：只使用密码的前72字节。
    对于更长的密码，我们使用SHA-256哈希预处理，
    这样可以保留长密码的安全性，同时符合bcrypt的限制。
    
    Args:
        password: 原始密码字符串
        
    Returns:
        str: 处理后的密码（不超过72字节）
    """
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) > BCRYPT_MAX_LENGTH:
        return hashlib.sha256(password_bytes).hexdigest()
    
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希加密后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    processed_password = _preprocess_password(plain_password)
    return pwd_context.verify(processed_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码的哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 加密后的密码哈希
    """
    processed_password = _preprocess_password(password)
    return pwd_context.hash(processed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[dict]: 解码后的数据，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
