"""
安全认证模块
提供密码哈希、JWT令牌生成和验证等安全功能
"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

BCRYPT_MAX_BYTES = 72

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _preprocess_password(password: str) -> str:
    """
    预处理密码，解决bcrypt 72字节长度限制问题
    
    对于超过72字节的密码，先使用SHA-256哈希，
    产生64个字符的十六进制字符串（32字节），然后再进行bcrypt哈希。
    这样可以支持任意长度的密码，同时保持安全性。
    
    参数:
        password: 原始密码
    
    返回:
        str: 预处理后的密码
    """
    password_bytes = password.encode('utf-8')
    
    if len(password_bytes) > BCRYPT_MAX_BYTES:
        return hashlib.sha256(password_bytes).hexdigest()
    
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    将明文密码与哈希后的密码进行比对
    
    参数:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
    
    返回:
        bool: 密码是否匹配
    """
    processed_password = _preprocess_password(plain_password)
    return pwd_context.verify(processed_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    将明文密码转换为哈希值存储
    
    参数:
        password: 明文密码
    
    返回:
        str: 哈希后的密码
    """
    processed_password = _preprocess_password(password)
    return pwd_context.hash(processed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    生成包含用户信息的JWT令牌
    
    参数:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间
    
    返回:
        str: JWT令牌字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 生成JWT令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码JWT访问令牌
    验证并解析JWT令牌
    
    参数:
        token: JWT令牌字符串
    
    返回:
        Optional[dict]: 解析后的令牌数据，验证失败返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """
    生成API秘钥
    生成一个随机的32位秘钥
    
    返回:
        str: 生成的API秘钥
    """
    import secrets
    import string
    
    # 生成包含字母和数字的随机字符串
    characters = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(characters) for _ in range(32))
    
    return api_key
