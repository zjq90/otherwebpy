"""
认证路由模块
提供用户注册、登录、登出和JWT令牌管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, Token, ApiResponse
from security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

# OAuth2密码模式的令牌获取URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    用于需要认证的接口的依赖注入
    
    参数:
        token: JWT令牌
        db: 数据库会话
    
    返回:
        User: 当前用户对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 解码令牌
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # 获取用户名
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # 从数据库查询用户
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前激活用户
    检查用户是否激活
    
    参数:
        current_user: 当前用户
    
    返回:
        User: 激活的用户对象
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    获取当前管理员用户
    检查用户是否为管理员
    
    参数:
        current_user: 当前用户
    
    返回:
        User: 管理员用户对象
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


@router.post("/register", response_model=ApiResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    创建新用户账号
    
    参数:
        user_data: 用户注册数据
        db: 数据库会话
    
    返回:
        ApiResponse: 注册结果
    """
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他账号使用"
            )
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return ApiResponse(
        success=True,
        message="注册成功",
        data={"user": UserResponse.from_orm(new_user)}
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    使用OAuth2密码模式进行登录
    
    参数:
        form_data: 登录表单数据（用户名和密码）
        db: 数据库会话
    
    返回:
        Token: JWT访问令牌
    """
    # 查询用户
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 验证用户和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=ApiResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息接口
    返回当前登录用户的详细信息
    
    参数:
        current_user: 当前用户（通过依赖注入获取）
    
    返回:
        ApiResponse: 用户信息
    """
    return ApiResponse(
        success=True,
        message="获取成功",
        data={"user": UserResponse.from_orm(current_user)}
    )


@router.post("/logout", response_model=ApiResponse)
def logout():
    """
    用户登出接口
    注意：JWT是无状态的，这里只返回成功消息
    客户端需要自行删除存储的令牌
    
    返回:
        ApiResponse: 登出结果
    """
    return ApiResponse(
        success=True,
        message="登出成功"
    )
