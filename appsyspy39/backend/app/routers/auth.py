"""
认证路由 - 处理用户登录、登出和Token管理
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, Token, UserCreate
from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录接口
    
    - 使用OAuth2密码模式
    - 验证用户名和密码
    - 返回JWT访问令牌和用户信息
    
    Args:
        form_data: 包含username和password的表单数据
        db: 数据库会话
    
    Returns:
        Token: 包含access_token、token_type和user信息
    """
    # 查找用户
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    # 验证用户和密码
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    # 构建用户响应对象
    user_response = UserResponse.model_validate(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/register", response_model=UserResponse, summary="用户注册（管理员功能）")
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户注册接口
    
    - 仅管理员可以创建新用户
    - 密码会被哈希存储
    
    Args:
        user_data: 用户创建数据
        db: 数据库会话
        current_user: 当前登录用户（必须是管理员）
    
    Returns:
        UserResponse: 创建的用户信息
    """
    # 验证是否为管理员
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可以创建用户"
        )
    
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        phone=user_data.phone,
        role=user_data.role or "operator"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    
    Args:
        current_user: 当前登录用户（通过JWT验证获取）
    
    Returns:
        UserResponse: 用户信息
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", summary="修改密码")
async def change_password(
    old_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    修改当前用户密码
    
    Args:
        old_password: 旧密码
        new_password: 新密码
        db: 数据库会话
        current_user: 当前登录用户
    
    Returns:
        dict: 操作结果
    """
    # 验证旧密码
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 验证新密码长度
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(new_password)
    await db.commit()
    
    return {"success": True, "message": "密码修改成功"}
