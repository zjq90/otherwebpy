"""
JWT身份认证模块
实现用户登录认证、Token生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from app.config import settings


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer(auto_error=False)


class AuthService:
    """
    身份认证服务类
    
    提供密码哈希验证、JWT Token生成和验证功能
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希后的密码
            
        Returns:
            bool: 密码是否匹配
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        生成密码哈希
        
        Args:
            password: 明文密码
            
        Returns:
            str: 哈希后的密码
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建JWT访问令牌
        
        Args:
            data: 需要编码到Token的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT Token字符串
        """
        to_encode = data.copy()

        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                seconds=settings.JWT_ACCESS_TOKEN_EXPIRE_SECONDS
            )

        to_encode.update({"exp": expire})
        to_encode.update({"type": "access"})

        # 生成JWT
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        解码JWT访问令牌
        
        Args:
            token: JWT Token字符串
            
        Returns:
            Optional[Dict]: 解码后的数据，验证失败返回None
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # 验证Token类型
            if payload.get("type") != "access":
                logger.warning("无效的Token类型")
                return None

            return payload

        except JWTError as e:
            logger.debug(f"Token解码失败: {str(e)}")
            return None

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """
        从Token中获取用户ID
        
        Args:
            token: JWT Token
            
        Returns:
            Optional[int]: 用户ID，失败返回None
        """
        payload = AuthService.decode_access_token(token)
        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        try:
            return int(user_id)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """
        创建刷新Token(可选)
        
        Args:
            user_id: 用户ID
            
        Returns:
            str: 刷新Token
        """
        data = {
            "sub": str(user_id),
            "type": "refresh"
        }
        # 刷新Token有效期: 7天
        expires_delta = timedelta(days=7)
        return AuthService.create_access_token(data, expires_delta)


async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    获取当前用户ID(FastAPI依赖注入)
    
    用于需要登录认证的API端点
    
    Args:
        credentials: HTTP Bearer认证凭证
        
    Returns:
        int: 用户ID
        
    Raises:
        HTTPException: 认证失败时抛出
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_id = AuthService.get_user_id_from_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_optional_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[int]:
    """
    可选的用户ID获取(用于非必须登录的接口)
    
    与get_current_user_id不同，此函数在无Token或Token无效时返回None
    
    Args:
        credentials: HTTP Bearer认证凭证
        
    Returns:
        Optional[int]: 用户ID或None
    """
    if credentials is None:
        return None

    token = credentials.credentials
    return AuthService.get_user_id_from_token(token)
