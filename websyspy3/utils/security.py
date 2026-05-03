"""
安全工具模块
提供密码加密、JWT令牌生成和验证等功能
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib

from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


# 尝试导入bcrypt，如果没有则使用备用方案
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


def _preprocess_password(password: str) -> bytes:
    """
    预处理密码，处理bcrypt 72字节限制
    
    bcrypt只支持最多72字节的密码。为了支持更长的密码，
    我们先对密码进行SHA256哈希，得到64字节的十六进制字符串，
    这样可以支持任意长度的密码。
    
    参数:
        password: 明文密码
    
    返回:
        预处理后的密码字节
    """
    # 使用SHA256哈希密码，得到64字节的十六进制字符串
    # 这样可以支持任意长度的密码，同时避免超过bcrypt的72字节限制
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed.encode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    参数:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
    
    返回:
        密码是否匹配
    """
    if BCRYPT_AVAILABLE:
        # 预处理密码
        password_bytes = _preprocess_password(plain_password)
        # 确保哈希密码也是bytes
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    else:
        # 备用方案：使用SHA256（仅用于开发/测试）
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    参数:
        password: 明文密码
    
    返回:
        哈希后的密码
    """
    if BCRYPT_AVAILABLE:
        # 预处理密码
        password_bytes = _preprocess_password(password)
        # 生成盐并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    else:
        # 备用方案：使用SHA256（仅用于开发/测试）
        return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    参数:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间增量，如果为None则使用默认值
    
    返回:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 编码生成JWT令牌
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT访问令牌
    
    参数:
        token: JWT令牌字符串
    
    返回:
        解码后的数据，如果令牌无效则返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证JWT令牌并返回用户信息
    
    参数:
        token: JWT令牌字符串
    
    返回:
        用户信息字典，如果令牌无效则返回None
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    # 检查必要的字段
    user_id: int = payload.get("sub")
    username: str = payload.get("username")
    role: str = payload.get("role")
    
    if user_id is None or username is None:
        return None
    
    return {
        "user_id": int(user_id),
        "username": username,
        "role": role or "user"
    }


def sha256_hash(text: str) -> str:
    """
    使用SHA256算法哈希文本（用于向后兼容）
    
    参数:
        text: 要哈希的文本
    
    返回:
        SHA256哈希值
    """
    return hashlib.sha256(text.encode()).hexdigest()


def generate_reset_token(user_id: int, email: str) -> str:
    """
    生成密码重置令牌（可选功能）
    
    参数:
        user_id: 用户ID
        email: 用户邮箱
    
    返回:
        重置令牌
    """
    data = {
        "user_id": user_id,
        "email": email,
        "type": "password_reset"
    }
    # 重置令牌有效期为1小时
    expires = timedelta(hours=1)
    return create_access_token(data, expires_delta=expires)


def verify_reset_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证密码重置令牌
    
    参数:
        token: 重置令牌
    
    返回:
        令牌包含的数据，如果无效则返回None
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    # 检查令牌类型
    if payload.get("type") != "password_reset":
        return None
    
    return payload
