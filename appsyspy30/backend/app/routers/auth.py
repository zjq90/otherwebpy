"""
用户认证路由模块
处理用户注册、登录、Token刷新等功能
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, Invitation
from app.schemas import (
    UserCreate, UserLogin, UserUpdate, UserResponse, 
    Token, APIResponse
)
from app.auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_user, get_current_active_user
)
from app.config import settings
import random
import string

router = APIRouter(prefix="/auth", tags=["认证管理"])


def generate_invite_code(length: int = 8) -> str:
    """
    生成唯一邀请码
    
    Args:
        length: 邀请码长度
        
    Returns:
        str: 邀请码
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@router.post("/register", response_model=Token, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    - **username**: 用户名（3-50个字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少6个字符）
    - **nickname**: 昵称（可选）
    - **phone**: 手机号（可选）
    - **invite_code**: 邀请码（可选）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        or_(User.username == user_data.username, User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    
    # 处理邀请码
    inviter_id = None
    if user_data.invite_code:
        invitation = db.query(Invitation).filter(
            Invitation.invite_code == user_data.invite_code,
            Invitation.status == "pending"
        ).first()
        
        if invitation:
            inviter_id = invitation.inviter_id
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        nickname=user_data.nickname or user_data.username,
        bio=user_data.bio,
        phone=user_data.phone,
        points=100  # 新用户注册奖励积分
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 如果有邀请码，更新邀请记录
    if inviter_id and user_data.invite_code:
        invitation = db.query(Invitation).filter(
            Invitation.invite_code == user_data.invite_code
        ).first()
        
        if invitation:
            invitation.invitee_id = new_user.id
            invitation.status = "registered"
            db.commit()
        
        # 给邀请者奖励积分
        inviter = db.query(User).filter(User.id == inviter_id).first()
        if inviter:
            inviter.points += 200  # 邀请奖励积分
            db.commit()
    
    # 生成访问令牌
    access_token = create_access_token(
        data={"user_id": new_user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    # 根据用户名或邮箱查找用户
    user = db.query(User).filter(
        or_(User.username == login_data.username, User.email == login_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(login_data.password, user.hashed_password):
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
    
    # 生成访问令牌
    access_token = create_access_token(
        data={"user_id": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的信息
    需要认证
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的信息
    需要认证
    """
    # 更新用户信息
    update_data = user_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=APIResponse, summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    用户登出接口
    客户端只需删除本地Token即可
    """
    return APIResponse(
        code=200,
        message="登出成功",
        data={"user_id": current_user.id}
    )


@router.post("/refresh", response_model=Token, summary="刷新Token")
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    刷新访问令牌
    需要认证
    """
    # 生成新的访问令牌
    access_token = create_access_token(
        data={"user_id": current_user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(current_user)
    )
