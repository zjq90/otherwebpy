"""
用户认证路由模块
包含注册、登录、找回密码、用户信息管理等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from datetime import datetime
from typing import Optional, List
import logging

from app.database import get_db
from app.models import User, UserAddress, Invite, PointsTransaction, PointsConfig
from app.schemas.user import (
    PhoneRegisterRequest, ThirdPartyLoginRequest,
    PhoneLoginRequest, SmsLoginRequest, LoginResponse,
    ForgotPasswordRequest, SendSmsRequest,
    UserInfo, UpdateUserInfoRequest, ChangePasswordRequest,
    UserAddressCreate, UserAddressUpdate, UserAddressResponse,
    RefreshTokenRequest
)
from app.schemas.common import success, success_page, error, ERROR_CODES
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token,
    decode_token, generate_sms_code, generate_invite_code
)
from app.utils.dependencies import get_current_user, get_pagination_params

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["用户认证"])

# 模拟验证码存储（实际项目应该使用Redis）
_sms_codes = {}


@router.post("/register")
async def register(
    request: PhoneRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手机号注册
    支持手机号+密码+验证码注册，可选邀请码
    """
    # 1. 验证手机号是否已注册
    result = await db.execute(select(User).where(User.phone == request.phone))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return error(code=1003, message=ERROR_CODES[1003])
    
    # 2. 验证验证码（模拟，实际项目应从Redis获取）
    cache_key = f"{request.phone}:register"
    if cache_key not in _sms_codes or _sms_codes[cache_key] != request.sms_code:
        # 测试环境允许万能验证码
        if request.sms_code != "123456":
            return error(code=1004, message=ERROR_CODES[1004])
    
    # 3. 处理邀请码
    inviter_id = None
    if request.invite_code:
        result = await db.execute(select(User).where(User.invite_code == request.invite_code))
        inviter = result.scalar_one_or_none()
        if inviter:
            inviter_id = inviter.id
    
    # 4. 创建用户
    hashed_password = get_password_hash(request.password)
    
    # 生成唯一邀请码
    invite_code = generate_invite_code()
    while True:
        result = await db.execute(select(User).where(User.invite_code == invite_code))
        if not result.scalar_one_or_none():
            break
        invite_code = generate_invite_code()
    
    new_user = User(
        phone=request.phone,
        password=hashed_password,
        nickname=request.nickname or f"用户{request.phone[-4:]}",
        invite_code=invite_code,
        invited_by=inviter_id,
        register_time=datetime.now()
    )
    
    db.add(new_user)
    await db.flush()  # 获取用户ID
    
    # 5. 处理邀请关系
    if inviter_id:
        invite_record = Invite(
            inviter_id=inviter_id,
            invitee_id=new_user.id,
            invite_code=request.invite_code,
            status=1
        )
        db.add(invite_record)
    
    # 6. 新用户注册积分奖励
    result = await db.execute(select(PointsConfig).where(PointsConfig.config_key == "new_user_bonus"))
    bonus_config = result.scalar_one_or_none()
    bonus_points = int(bonus_config.config_value) if bonus_config else 100
    
    if bonus_points > 0:
        new_user.points += bonus_points
        new_user.total_points += bonus_points
        
        # 记录积分交易
        transaction = PointsTransaction(
            user_id=new_user.id,
            transaction_type="new_user",
            transaction_type_text="新用户奖励",
            points=bonus_points,
            balance_after=new_user.points,
            description="新用户注册积分奖励"
        )
        db.add(transaction)
    
    await db.commit()
    await db.refresh(new_user)
    
    # 7. 生成登录令牌
    access_token = create_access_token(subject=new_user.id)
    refresh_token = create_refresh_token(subject=new_user.id)
    
    return success(
        data=LoginResponse(
            user_id=new_user.id,
            phone=new_user.phone,
            nickname=new_user.nickname,
            avatar=new_user.avatar,
            access_token=access_token,
            refresh_token=refresh_token
        ),
        message="注册成功"
    )


@router.post("/login")
async def login(
    request: PhoneLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手机号密码登录
    """
    # 1. 查找用户
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()
    
    if not user:
        return error(code=1001, message=ERROR_CODES[1001])
    
    # 2. 验证密码
    if not verify_password(request.password, user.password):
        return error(code=1002, message=ERROR_CODES[1002])
    
    # 3. 检查用户状态
    if user.status != 1:
        return error(code=1005, message=ERROR_CODES[1005])
    
    # 4. 更新登录时间
    user.last_login_time = datetime.now()
    await db.commit()
    
    # 5. 生成令牌
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return success(
        data=LoginResponse(
            user_id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            access_token=access_token,
            refresh_token=refresh_token
        ),
        message="登录成功"
    )


@router.post("/login/sms")
async def login_by_sms(
    request: SmsLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手机号验证码登录
    如果用户不存在，自动注册
    """
    # 1. 验证验证码
    cache_key = f"{request.phone}:login"
    if cache_key not in _sms_codes or _sms_codes[cache_key] != request.sms_code:
        if request.sms_code != "123456":
            return error(code=1004, message=ERROR_CODES[1004])
    
    # 2. 查找用户
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()
    
    # 3. 如果用户不存在，自动注册
    if not user:
        # 生成唯一邀请码
        invite_code = generate_invite_code()
        while True:
            result = await db.execute(select(User).where(User.invite_code == invite_code))
            if not result.scalar_one_or_none():
                break
            invite_code = generate_invite_code()
        
        user = User(
            phone=request.phone,
            nickname=f"用户{request.phone[-4:]}",
            invite_code=invite_code,
            register_time=datetime.now()
        )
        db.add(user)
        await db.flush()
        
        # 新用户积分奖励
        result = await db.execute(select(PointsConfig).where(PointsConfig.config_key == "new_user_bonus"))
        bonus_config = result.scalar_one_or_none()
        bonus_points = int(bonus_config.config_value) if bonus_config else 100
        
        if bonus_points > 0:
            user.points += bonus_points
            user.total_points += bonus_points
            
            transaction = PointsTransaction(
                user_id=user.id,
                transaction_type="new_user",
                transaction_type_text="新用户奖励",
                points=bonus_points,
                balance_after=user.points,
                description="新用户注册积分奖励"
            )
            db.add(transaction)
        
        await db.commit()
        await db.refresh(user)
    else:
        # 检查用户状态
        if user.status != 1:
            return error(code=1005, message=ERROR_CODES[1005])
        
        # 更新登录时间
        user.last_login_time = datetime.now()
        await db.commit()
    
    # 4. 生成令牌
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return success(
        data=LoginResponse(
            user_id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            access_token=access_token,
            refresh_token=refresh_token
        ),
        message="登录成功"
    )


@router.post("/login/third-party")
async def login_by_third_party(
    request: ThirdPartyLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    第三方登录（微信/支付宝）
    模拟实现，实际需要调用第三方SDK
    """
    # 模拟第三方登录
    # 实际项目中需要根据code调用微信/支付宝接口获取openid
    
    mock_openid = f"{request.login_type}_{request.code}"
    
    # 1. 检查是否已绑定
    from app.models import LoginMethod
    result = await db.execute(
        select(LoginMethod).where(
            LoginMethod.login_type == request.login_type,
            LoginMethod.openid == mock_openid
        )
    )
    login_method = result.scalar_one_or_none()
    
    if login_method:
        # 已绑定，直接登录
        result = await db.execute(select(User).where(User.id == login_method.user_id))
        user = result.scalar_one()
        
        if user.status != 1:
            return error(code=1005, message=ERROR_CODES[1005])
        
        user.last_login_time = datetime.now()
        await db.commit()
    else:
        # 未绑定，创建新用户
        invite_code = generate_invite_code()
        while True:
            result = await db.execute(select(User).where(User.invite_code == invite_code))
            if not result.scalar_one_or_none():
                break
            invite_code = generate_invite_code()
        
        inviter_id = None
        if request.invite_code:
            result = await db.execute(select(User).where(User.invite_code == request.invite_code))
            inviter = result.scalar_one_or_none()
            if inviter:
                inviter_id = inviter.id
        
        user = User(
            phone=f"third_{mock_openid}",
            nickname=f"{request.login_type}用户",
            invite_code=invite_code,
            invited_by=inviter_id,
            register_time=datetime.now()
        )
        db.add(user)
        await db.flush()
        
        # 创建登录方式记录
        login_method = LoginMethod(
            user_id=user.id,
            login_type=request.login_type,
            openid=mock_openid
        )
        db.add(login_method)
        
        # 处理邀请
        if inviter_id:
            invite_record = Invite(
                inviter_id=inviter_id,
                invitee_id=user.id,
                invite_code=request.invite_code,
                status=1
            )
            db.add(invite_record)
        
        # 新用户积分奖励
        result = await db.execute(select(PointsConfig).where(PointsConfig.config_key == "new_user_bonus"))
        bonus_config = result.scalar_one_or_none()
        bonus_points = int(bonus_config.config_value) if bonus_config else 100
        
        if bonus_points > 0:
            user.points += bonus_points
            user.total_points += bonus_points
            
            transaction = PointsTransaction(
                user_id=user.id,
                transaction_type="new_user",
                transaction_type_text="新用户奖励",
                points=bonus_points,
                balance_after=user.points,
                description="新用户注册积分奖励"
            )
            db.add(transaction)
        
        await db.commit()
        await db.refresh(user)
    
    # 生成令牌
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return success(
        data=LoginResponse(
            user_id=user.id,
            phone=user.phone,
            nickname=user.nickname,
            avatar=user.avatar,
            access_token=access_token,
            refresh_token=refresh_token
        ),
        message="登录成功"
    )


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    忘记密码
    通过手机号验证码重置密码
    """
    # 1. 查找用户
    result = await db.execute(select(User).where(User.phone == request.phone))
    user = result.scalar_one_or_none()
    
    if not user:
        return error(code=1001, message=ERROR_CODES[1001])
    
    # 2. 验证验证码
    cache_key = f"{request.phone}:reset_password"
    if cache_key not in _sms_codes or _sms_codes[cache_key] != request.sms_code:
        if request.sms_code != "123456":
            return error(code=1004, message=ERROR_CODES[1004])
    
    # 3. 更新密码
    user.password = get_password_hash(request.new_password)
    await db.commit()
    
    return success(message="密码重置成功")


@router.post("/send-sms")
async def send_sms(
    request: SendSmsRequest
):
    """
    发送短信验证码
    模拟实现，实际项目需要调用短信服务商API
    """
    # 生成验证码
    sms_code = generate_sms_code()
    
    # 存储验证码（5分钟过期）
    cache_key = f"{request.phone}:{request.sms_type}"
    _sms_codes[cache_key] = sms_code
    
    logger.info(f"发送验证码: {request.phone} -> {sms_code}, 类型: {request.sms_type}")
    
    # 实际项目中调用短信服务商API
    # await send_sms_service(request.phone, sms_code)
    
    return success(
        data={
            "phone": request.phone,
            "sms_type": request.sms_type,
            "expire_minutes": 5,
            "test_code": sms_code  # 测试环境返回验证码，生产环境删除
        },
        message="验证码发送成功"
    )


@router.post("/refresh-token")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    """
    # 1. 验证刷新令牌
    payload = decode_token(request.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期"
        )
    
    user_id = int(payload.get("sub"))
    
    # 2. 查找用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 3. 生成新的访问令牌
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return success(
        data={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        },
        message="令牌刷新成功"
    )


@router.get("/info", response_model=UserInfo)
async def get_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    return current_user


@router.put("/info")
async def update_user_info(
    request: UpdateUserInfoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新用户信息
    """
    update_data = request.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return success(data=current_user.to_dict(), message="更新成功")


@router.put("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    """
    # 验证原密码
    if not current_user.password:
        # 如果没有密码（第三方登录用户），直接设置新密码
        current_user.password = get_password_hash(request.new_password)
    elif not verify_password(request.old_password, current_user.password):
        return error(code=1002, message=ERROR_CODES[1002])
    else:
        current_user.password = get_password_hash(request.new_password)
    
    await db.commit()
    
    return success(message="密码修改成功")


# ==================== 地址管理 ====================

@router.get("/addresses")
async def get_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户地址列表
    """
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.user_id == current_user.id,
            UserAddress.status == 1
        ).order_by(UserAddress.is_default.desc(), UserAddress.create_time.desc())
    )
    addresses = result.scalars().all()
    
    return success(data=[addr.to_dict() for addr in addresses])


@router.get("/addresses/default")
async def get_default_address(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取默认地址
    """
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.user_id == current_user.id,
            UserAddress.status == 1,
            UserAddress.is_default == 1
        )
    )
    address = result.scalar_one_or_none()
    
    if address:
        return success(data=address.to_dict())
    else:
        # 返回第一个地址
        result = await db.execute(
            select(UserAddress).where(
                UserAddress.user_id == current_user.id,
                UserAddress.status == 1
            ).order_by(UserAddress.create_time.desc())
        )
        address = result.scalar_one_or_none()
        return success(data=address.to_dict() if address else None)


@router.post("/addresses")
async def create_address(
    request: UserAddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建地址
    """
    # 如果设置为默认，先取消其他地址的默认状态
    if request.is_default:
        await db.execute(
            update(UserAddress).where(
                UserAddress.user_id == current_user.id
            ).values(is_default=0)
        )
    
    new_address = UserAddress(
        user_id=current_user.id,
        name=request.name,
        phone=request.phone,
        province=request.province,
        city=request.city,
        district=request.district,
        address=request.address,
        is_default=1 if request.is_default else 0
    )
    
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    
    return success(data=new_address.to_dict(), message="地址添加成功")


@router.put("/addresses/{address_id}")
async def update_address(
    address_id: int,
    request: UserAddressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新地址
    """
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()
    
    if not address:
        return error(code=404, message="地址不存在")
    
    # 如果设置为默认，先取消其他地址的默认状态
    if request.is_default:
        await db.execute(
            update(UserAddress).where(
                UserAddress.user_id == current_user.id
            ).values(is_default=0)
        )
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(address, key, value)
    
    await db.commit()
    await db.refresh(address)
    
    return success(data=address.to_dict(), message="地址更新成功")


@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除地址（软删除）
    """
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()
    
    if not address:
        return error(code=404, message="地址不存在")
    
    address.status = 0
    await db.commit()
    
    return success(message="地址删除成功")


@router.put("/addresses/{address_id}/set-default")
async def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    设置默认地址
    """
    result = await db.execute(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_id == current_user.id
        )
    )
    address = result.scalar_one_or_none()
    
    if not address:
        return error(code=404, message="地址不存在")
    
    # 取消其他地址的默认状态
    await db.execute(
        update(UserAddress).where(
            UserAddress.user_id == current_user.id
        ).values(is_default=0)
    )
    
    address.is_default = 1
    await db.commit()
    
    return success(message="设置默认地址成功")
