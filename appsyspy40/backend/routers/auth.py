"""
用户认证路由
包含登录、注册、获取用户信息等功能
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db, settings
from core.security import (
    verify_password, get_password_hash, create_access_token,
    get_current_user
)
from models.models import User
from schemas.schemas import (
    UserCreate, UserResponse, Token, ApiResponse
)


router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=ApiResponse, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    创建新用户账号
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
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
        role=user_data.role,
        phone=user_data.phone,
        email=user_data.email
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return ApiResponse(
        code=200,
        message="注册成功",
        data={"user": UserResponse.model_validate(new_user).model_dump()}
    )


@router.post("/login", response_model=ApiResponse, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录
    验证用户身份并返回JWT令牌
    """
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
    
    return ApiResponse(
        code=200,
        message="登录成功",
        data=token_data.model_dump()
    )


@router.get("/me", response_model=ApiResponse, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    需要认证
    """
    return ApiResponse(
        code=200,
        message="success",
        data={"user": UserResponse.model_validate(current_user).model_dump()}
    )


@router.put("/me", response_model=ApiResponse, summary="更新当前用户信息")
async def update_current_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前登录用户的信息
    需要认证
    """
    # 检查用户名是否被其他用户使用
    if user_data.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
    
    # 更新用户信息
    current_user.username = user_data.username
    current_user.real_name = user_data.real_name
    current_user.phone = user_data.phone
    current_user.email = user_data.email
    
    # 如果提供了新密码，则更新密码
    if user_data.password:
        current_user.password_hash = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(current_user)
    
    return ApiResponse(
        code=200,
        message="更新成功",
        data={"user": UserResponse.model_validate(current_user).model_dump()}
    )
