"""
认证相关API路由
处理用户登录、获取当前用户信息、获取用户权限等
"""

from datetime import datetime, timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings
from app.crud.user import user_crud
from app.crud.permission import permission_crud
from app.models.user import User
from app.schemas.user import UserLogin, UserResponse, UserWithRoles
from app.schemas.token import Token
from app.schemas.common import ResponseModel
from app.middleware.auth_middleware import get_current_user, get_current_active_user


router = APIRouter()


@router.post("/login", response_model=ResponseModel[Token], summary="用户登录")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    用户登录接口
    
    验证用户名和密码，成功后返回JWT访问令牌
    
    参数:
        user_data: 登录数据（用户名和密码）
        db: 数据库会�?
    
    返回:
        包含JWT令牌的响�?
    """
    # 验证用户凭据
    user = user_crud.authenticate(db, username=user_data.username, password=user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 更新最后登录时�?
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    
    # 创建JWT令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    # 构造令牌响�?
    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return ResponseModel(
        code=200,
        message="登录成功",
        data=token
    )


@router.get("/current-user", response_model=ResponseModel[UserWithRoles], summary="获取当前用户信息")
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取当前登录用户的详细信�?
    
    需要有效的JWT令牌
    
    参数:
        current_user: 当前登录用户（由中间件自动获取）
        db: 数据库会�?
    
    返回:
        当前用户的详细信息，包括角色
    """
    # 构建用户响应数据，包含角色信�?
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "last_login": current_user.last_login,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "description": role.description
            }
            for role in current_user.roles
        ]
    }
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=user_data
    )


@router.get("/me/permissions", response_model=ResponseModel[List[dict]], summary="获取当前用户权限")
def get_my_permissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    获取当前登录用户的所有权�?
    
    需要有效的JWT令牌
    
    参数:
        current_user: 当前登录用户
        db: 数据库会�?
    
    返回:
        当前用户拥有的所有权限列�?
    """
    # 超级管理员返回所有权�?
    if current_user.is_superuser:
        permissions, _ = permission_crud.get_multi(db, skip=0, limit=1000)
    else:
        # 获取用户的所有权�?
        permissions = permission_crud.get_permissions_by_user_id(db, user_id=current_user.id)
    
    # 构建权限响应数据
    permission_data = [
        {
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "description": perm.description,
            "module": perm.module,
            "action": perm.action
        }
        for perm in permissions
    ]
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data=permission_data
    )


@router.post("/logout", response_model=ResponseModel[dict], summary="用户登出")
def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    用户登出接口
    
    注意：由于JWT是无状态的，服务器端无法直接使令牌失效�?
    这里主要做一些清理工作，实际的令牌失效需要客户端自行处理�?
    
    参数:
        current_user: 当前登录用户
    
    返回:
        登出成功响应
    """
    return ResponseModel(
        code=200,
        message="登出成功",
        data={"detail": "请在客户端清除本地存储的令牌"}
    )


@router.post("/refresh-token", response_model=ResponseModel[Token], summary="刷新令牌")
def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
) -> Any:
    """
    刷新JWT令牌
    
    使用有效的旧令牌获取新的令牌
    
    参数:
        credentials: HTTP认证凭证（包含旧令牌�?
        db: 数据库会�?
    
    返回:
        新的JWT令牌
    """
    # 解码旧令�?
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令�?
        )
    
    # 获取用户ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌载�?
        )
    
    # 获取用户
    user = user_crud.get_by_id(db, user_id=int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的JWT令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    # 构造令牌响�?
    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return ResponseModel(
        code=200,
        message="令牌刷新成功",
        data=token
    )
