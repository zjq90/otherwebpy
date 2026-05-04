"""
认证中间�?
处理JWT认证、用户获取和权限检�?
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.crud.user import user_crud
from app.models.user import User


# HTTP Bearer 认证方案
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    从JWT令牌中解析用户信息并从数据库获取完整用户对象
    
    参数:
        credentials: HTTP认证凭证
        db: 数据库会�?
    
    返回:
        当前登录的用户对�?
    
    异常:
        HTTPException: 认证失败时抛�?
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # 从载荷中获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    user = user_crud.get_by_id(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    检查用户是否被激�?
    
    参数:
        current_user: 当前用户（由get_current_user提供�?
    
    返回:
        当前活跃的用户对�?
    
    异常:
        HTTPException: 用户未激活时抛出
    """
    if not user_crud.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    return current_user


def require_permission(permission_code: str):
    """
    权限检查装饰器工厂
    用于创建检查用户是否拥有指定权限的依赖�?
    
    参数:
        permission_code: 权限代码（如 "user:create", "role:delete"�?
    
    返回:
        一个依赖项函数，用于检查当前用户是否拥有指定权�?
    
    用法示例:
        @router.post("/users/")
        def create_user(
            ...,
            current_user: User = Depends(require_permission("user:create"))
        ):
            ...
    """
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        """
        权限检查函�?
        
        参数:
            current_user: 当前活跃用户
            db: 数据库会�?
        
        返回:
            检查通过后返回当前用户对�?
        
        异常:
            HTTPException: 权限不足时抛�?
        """
        # 超级管理员拥有所有权�?
        if current_user.is_superuser:
            return current_user
        
        # 检查用户是否拥有指定权�?
        if not current_user.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需�?{permission_code} 权限"
            )
        
        return current_user
    
    return permission_checker


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    获取当前登录用户（可选）
    与get_current_user不同，这个函数在没有认证信息时不会抛出异常，而是返回None
    
    参数:
        credentials: HTTP认证凭证（可选）
        db: 数据库会�?
    
    返回:
        如果有有效认证则返回用户对象，否则返回None
    """
    if credentials is None:
        return None
    
    try:
        # 解码JWT令牌
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            return None
        
        # 从载荷中获取用户ID
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        # 从数据库获取用户
        user = user_crud.get_by_id(db, user_id=int(user_id))
        return user
    except Exception:
        return None
