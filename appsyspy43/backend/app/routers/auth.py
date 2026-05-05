"""
认证路由模块
处理用户登录、登出、令牌刷新等认证相关操作
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserStatus
from app.schemas.user import UserLogin, UserLoginResponse, UserResponse
from app.schemas.common import ApiResponse, Token
from app.utils.security import (
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["认证管理"],
    responses={404: {"description": "未找到"}},
)


@router.post("/login", response_model=ApiResponse[UserLoginResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录接口
    使用用户名和密码进行登录，返回JWT访问令牌
    """
    # 根据用户名查询用户
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    # 验证用户是否存在和密码是否正确
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，请联系管理员"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value,
        },
        expires_delta=access_token_expires,
    )
    
    # 构建响应数据
    user_response = UserResponse.model_validate(user)
    login_response = UserLoginResponse(
        user=user_response,
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data=login_response,
    )


@router.post("/login-password", response_model=ApiResponse[UserLoginResponse])
async def login_with_password(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录接口（JSON格式）
    使用用户名和密码进行登录，返回JWT访问令牌
    """
    # 根据用户名查询用户
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    
    # 验证用户是否存在和密码是否正确
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，请联系管理员"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value,
        },
        expires_delta=access_token_expires,
    )
    
    # 构建响应数据
    user_response = UserResponse.model_validate(user)
    login_response = UserLoginResponse(
        user=user_response,
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data=login_response,
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    获取当前登录用户信息
    需要有效的JWT令牌才能访问
    """
    user_response = UserResponse.model_validate(current_user)
    return ApiResponse(
        code=200,
        message="获取成功",
        data=user_response,
    )


@router.post("/refresh", response_model=ApiResponse[Token])
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """
    刷新访问令牌
    使用现有的有效令牌获取新的访问令牌
    """
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": current_user.id,
            "role": current_user.role.value,
        },
        expires_delta=access_token_expires,
    )
    
    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return ApiResponse(
        code=200,
        message="令牌刷新成功",
        data=token,
    )


@router.post("/logout", response_model=ApiResponse[dict])
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    用户登出接口
    注意：JWT是无状态的，此接口主要用于客户端清除令牌
    """
    return ApiResponse(
        code=200,
        message="登出成功",
        data={},
    )
