"""
认证路由模块
处理用户注册、登录、令牌刷新等认证相关操作
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, UserRole
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    ResponseModel
)
from utils import (
    verify_password, get_password_hash, create_access_token,
    decode_access_token, get_current_active_user
)
from config import settings

router = APIRouter()

# ========================================
# 注册
# ========================================

@router.post("/register", response_model=ResponseModel)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    
    支持会员、教练等角色的注册
    用户名和手机号必须唯一
    
    Args:
        user_data: 用户注册数据
        db: 数据库会话
        
    Returns:
        ResponseModel: 包含用户信息的响应
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已存在
    existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被注册"
        )
    
    # 检查邮箱是否已存在（如果提供了邮箱）
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        phone=user_data.phone,
        real_name=user_data.real_name,
        avatar=user_data.avatar,
        gender=user_data.gender,
        role=user_data.role if user_data.role else UserRole.MEMBER,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 构建响应数据
    user_response = UserResponse.model_validate(new_user)
    
    return ResponseModel(
        code=200,
        message="注册成功",
        data={"user": user_response.model_dump()}
    )

# ========================================
# 登录
# ========================================

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    
    支持用户名或手机号登录
    登录成功后返回JWT令牌
    
    Args:
        login_data: 登录数据
        db: 数据库会话
        
    Returns:
        Token: 包含访问令牌的响应
    """
    # 查找用户（支持用户名或手机号登录）
    user = None
    
    if login_data.username:
        user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user and login_data.phone:
        user = db.query(User).filter(User.phone == login_data.phone).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员"
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        }
    )
    
    # 计算过期时间（秒）
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    # 构建用户响应
    user_response = UserResponse.model_validate(user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_response
    )

# ========================================
# 获取当前用户信息
# ========================================

@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户的信息
    
    需要有效的JWT令牌
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        ResponseModel: 包含用户信息的响应
    """
    user_response = UserResponse.model_validate(current_user)
    
    return ResponseModel(
        code=200,
        message="获取成功",
        data={"user": user_response.model_dump()}
    )

# ========================================
# 刷新令牌
# ========================================

@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    使用当前有效的令牌获取新的令牌
    延长登录有效期
    
    Args:
        credentials: HTTP授权凭证
        db: 数据库会话
        
    Returns:
        Token: 包含新令牌的响应
    """
    # 解码现有令牌
    token_data = decode_access_token(credentials.credentials)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建新的访问令牌
    new_access_token = create_access_token(
        data={
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        }
    )
    
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user_response = UserResponse.model_validate(user)
    
    return Token(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_response
    )

# ========================================
# 登出
# ========================================

@router.post("/logout", response_model=ResponseModel)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    用户登出接口
    
    注意：由于JWT是无状态的，服务端无法直接使令牌失效
    实际登出需要客户端删除本地存储的令牌
    此接口主要用于记录登出行为和清理服务端缓存（如果有）
    
    Args:
        current_user: 当前认证用户
        
    Returns:
        ResponseModel: 登出成功响应
    """
    # TODO: 如果有使用Redis等存储活跃令牌，可以在此处删除
    
    return ResponseModel(
        code=200,
        message="登出成功",
        data=None
    )

# ========================================
# 修改密码
# ========================================

@router.post("/change-password", response_model=ResponseModel)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改用户密码
    
    Args:
        old_password: 旧密码
        new_password: 新密码
        current_user: 当前认证用户
        db: 数据库会话
        
    Returns:
        ResponseModel: 操作结果
    """
    # 验证旧密码
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 验证新密码长度
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return ResponseModel(
        code=200,
        message="密码修改成功",
        data=None
    )
