"""
认证相关API路由
包含登录、注册、实名认证等功能
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_

from ..database import get_db
from ..models.user_models import User, Role, VerificationCode
from ..schemas.user_schemas import (
    PasswordLoginRequest, PhoneLoginRequest, SendCodeRequest,
    LoginResponse, RealNameVerifyRequest, UserResponse,
    ChangePasswordRequest, ApiResponse
)
from ..utils.security import (
    verify_password, get_password_hash, create_access_token,
    generate_verification_code, get_current_user, get_user_permissions
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/send-code", response_model=ApiResponse)
async def send_verification_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发送验证码
    用于手机号验证码登录
    注意：生产环境应集成短信服务发送真实验证码
    """
    # 生成6位验证码
    code = generate_verification_code()
    
    # 计算过期时间
    expires_at = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
    
    # 检查是否已有未使用的验证码
    result = await db.execute(
        select(VerificationCode).where(
            and_(
                VerificationCode.phone == request.phone,
                VerificationCode.is_used == False,
                VerificationCode.expires_at > datetime.utcnow()
            )
        )
    )
    existing_code = result.scalar_one_or_none()
    
    if existing_code:
        # 更新现有验证码
        existing_code.code = code
        existing_code.expires_at = expires_at
    else:
        # 创建新验证码
        verification_code = VerificationCode(
            phone=request.phone,
            code=code,
            expires_at=expires_at
        )
        db.add(verification_code)
    
    await db.commit()
    
    # 开发环境直接返回验证码，生产环境应通过短信发送
    return ApiResponse(
        message="验证码已发送",
        data={"code": code, "phone": request.phone}
    )


@router.post("/login/password", response_model=LoginResponse)
async def login_with_password(
    request: PasswordLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    账号密码登录
    """
    # 查询用户及角色
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # 创建访问令牌
    access_token = create_access_token(data={"user_id": user.id, "username": user.username})
    
    # 构建用户响应
    user_response = UserResponse.model_validate(user)
    
    return LoginResponse(
        access_token=access_token,
        user=user_response,
        is_first_login=user.is_first_login
    )


@router.post("/login/phone", response_model=LoginResponse)
async def login_with_phone(
    request: PhoneLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手机号验证码登录
    """
    # 验证验证码
    result = await db.execute(
        select(VerificationCode).where(
            and_(
                VerificationCode.phone == request.phone,
                VerificationCode.code == request.code,
                VerificationCode.is_used == False,
                VerificationCode.expires_at > datetime.utcnow()
            )
        )
    )
    verification_code = result.scalar_one_or_none()
    
    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="验证码无效或已过期"
        )
    
    # 标记验证码已使用
    verification_code.is_used = True
    
    # 查询用户及角色
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.phone == request.phone)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # 如果用户不存在，创建新用户（自动注册）
        user = User(
            phone=request.phone,
            is_first_login=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await db.commit()
    
    # 创建访问令牌
    access_token = create_access_token(data={"user_id": user.id})
    
    # 构建用户响应
    user_response = UserResponse.model_validate(user)
    
    return LoginResponse(
        access_token=access_token,
        user=user_response,
        is_first_login=user.is_first_login
    )


@router.post("/real-name-verify", response_model=ApiResponse)
async def real_name_verification(
    request: RealNameVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    实名认证
    首次登录后需要完成实名认证
    """
    # 简单的身份证号格式验证
    if len(request.id_card) not in [15, 18]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号格式不正确"
        )
    
    # 更新用户信息
    current_user.real_name = request.real_name
    current_user.id_card = request.id_card
    current_user.is_verified = True
    current_user.is_first_login = False
    
    await db.commit()
    
    return ApiResponse(message="实名认证成功")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    """
    return UserResponse.model_validate(current_user)


@router.get("/permissions")
async def get_current_user_permissions(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的权限列表
    """
    permissions = get_user_permissions(current_user)
    return {"permissions": permissions}


@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    """
    if not current_user.password_hash or not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(request.new_password)
    await db.commit()
    
    return ApiResponse(message="密码修改成功")


@router.post("/logout", response_model=ApiResponse)
async def logout():
    """
    退出登录
    注意：JWT是无状态的，退出登录需要客户端删除令牌
    """
    return ApiResponse(message="退出登录成功")
