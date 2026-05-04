"""
认证路由模块
包含用户注册、登录、微信登录等认证相关接口
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate, UserLogin, WechatLogin, UserUpdate,
    UserResponse, Token
)
from app.utils.security import (
    get_password_hash, verify_password, create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["认证管理"])
security = HTTPBearer()


@router.post("/register", response_model=Token, summary="用户注册")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    新用户注册
    
    - **username**: 用户名（2-50字符）
    - **password**: 密码（6-100字符）
    - **real_name**: 真实姓名（可选）
    - **phone**: 手机号（可选）
    - **email**: 邮箱（可选）
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查手机号是否已绑定（如果提供了手机号）
    if user_data.phone:
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被绑定"
            )
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        real_name=user_data.real_name,
        phone=user_data.phone,
        email=user_data.email,
        is_active=True,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 生成访问令牌
    access_token = create_access_token(subject=new_user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token, summary="用户登录")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录（用户名+密码）
    
    - **username**: 用户名
    - **password**: 密码
    """
    # 查找用户
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.now()
    db.commit()
    db.refresh(user)
    
    # 生成访问令牌
    access_token = create_access_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/wechat-login", response_model=Token, summary="微信登录")
def wechat_login(wechat_data: WechatLogin, db: Session = Depends(get_db)):
    """
    微信一键登录
    
    - **code**: 微信登录授权码
    
    注意：这里模拟微信登录流程，实际生产环境需要调用微信API
    """
    # 模拟微信登录：根据code获取openid（实际应调用微信API）
    # 这里为了测试，直接将code作为模拟的openid
    mock_openid = f"wx_mock_{wechat_data.code}"
    
    # 查找已绑定微信的用户
    user = db.query(User).filter(User.wechat_openid == mock_openid).first()
    
    if user:
        # 用户已存在，直接登录
        user.last_login_at = datetime.now()
        db.commit()
        db.refresh(user)
    else:
        # 用户不存在，创建新用户并绑定微信
        username = f"微信用户_{mock_openid[-8:]}"
        user = User(
            username=username,
            password_hash=get_password_hash(mock_openid),  # 使用openid作为临时密码
            wechat_openid=mock_openid,
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 生成访问令牌
    access_token = create_access_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    需要携带有效的Bearer Token
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
def update_current_user_info(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前登录用户的信息
    
    - **real_name**: 真实姓名
    - **avatar**: 头像URL
    - **phone**: 手机号
    - **email**: 邮箱
    """
    # 检查手机号是否已被其他用户绑定
    if update_data.phone and update_data.phone != current_user.phone:
        existing_phone = db.query(User).filter(
            User.phone == update_data.phone,
            User.id != current_user.id
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被其他用户绑定"
            )
    
    # 更新用户信息
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/bind-phone", response_model=UserResponse, summary="绑定手机号")
def bind_phone(
    phone: str,
    verify_code: str,  # 验证码（生产环境需要验证）
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    绑定手机号到当前用户账户
    
    - **phone**: 手机号
    - **verify_code**: 验证码（测试环境可任意填写）
    """
    # 检查手机号是否已被绑定
    existing_user = db.query(User).filter(
        User.phone == phone,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号已被其他用户绑定"
        )
    
    # 绑定手机号
    current_user.phone = phone
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/bind-wechat", response_model=UserResponse, summary="绑定微信")
def bind_wechat(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    绑定微信账号到当前用户账户
    
    - **code**: 微信授权码
    """
    mock_openid = f"wx_mock_{code}"
    
    # 检查该微信是否已绑定其他账号
    existing_user = db.query(User).filter(
        User.wechat_openid == mock_openid,
        User.id != current_user.id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该微信已绑定其他账号"
        )
    
    # 绑定微信
    current_user.wechat_openid = mock_openid
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)
