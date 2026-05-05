"""
用户相关的Pydantic模型
用于请求和响应的数据验证
"""
from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ==================== 注册相关模型 ====================

class PhoneRegisterRequest(BaseModel):
    """
    手机号注册请求
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    sms_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    invite_code: Optional[str] = Field(None, description="邀请码")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 11:
            raise ValueError('手机号格式不正确')
        return v


class ThirdPartyLoginRequest(BaseModel):
    """
    第三方登录请求
    """
    login_type: str = Field(..., description="登录类型: wechat, alipay")
    code: str = Field(..., description="第三方授权码")
    invite_code: Optional[str] = Field(None, description="邀请码")


# ==================== 登录相关模型 ====================

class PhoneLoginRequest(BaseModel):
    """
    手机号密码登录请求
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")


class SmsLoginRequest(BaseModel):
    """
    手机号验证码登录请求
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    sms_code: str = Field(..., min_length=4, max_length=6, description="验证码")


class LoginResponse(BaseModel):
    """
    登录响应
    """
    user_id: int
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ==================== 忘记密码相关模型 ====================

class ForgotPasswordRequest(BaseModel):
    """
    忘记密码请求
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    sms_code: str = Field(..., min_length=4, max_length=6, description="验证码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


# ==================== 验证码请求模型 ====================

class SendSmsRequest(BaseModel):
    """
    发送验证码请求
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    sms_type: str = Field(..., description="验证码类型: register, login, reset_password")


# ==================== 用户信息模型 ====================

class UserInfo(BaseModel):
    """
    用户信息响应
    """
    id: int
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    email: Optional[str]
    gender: int = 0
    points: int = 0
    total_points: int = 0
    recycle_count: int = 0
    carbon_reduction: float = 0.0
    invite_code: Optional[str]
    invited_by: Optional[int]
    register_time: Optional[datetime]
    last_login_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class UpdateUserInfoRequest(BaseModel):
    """
    更新用户信息请求
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    email: Optional[str] = Field(None, description="邮箱")
    gender: Optional[int] = Field(None, description="性别: 0-未知, 1-男, 2-女")


class ChangePasswordRequest(BaseModel):
    """
    修改密码请求
    """
    old_password: str = Field(..., min_length=6, max_length=20, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


# ==================== 地址相关模型 ====================

class UserAddressCreate(BaseModel):
    """
    创建地址请求
    """
    name: str = Field(..., max_length=50, description="收货人姓名")
    phone: str = Field(..., min_length=11, max_length=11, description="电话")
    province: Optional[str] = Field(None, description="省")
    city: Optional[str] = Field(None, description="市")
    district: Optional[str] = Field(None, description="区")
    address: str = Field(..., max_length=255, description="详细地址")
    is_default: bool = Field(False, description="是否默认地址")


class UserAddressUpdate(BaseModel):
    """
    更新地址请求
    """
    name: Optional[str] = Field(None, max_length=50, description="收货人姓名")
    phone: Optional[str] = Field(None, min_length=11, max_length=11, description="电话")
    province: Optional[str] = Field(None, description="省")
    city: Optional[str] = Field(None, description="市")
    district: Optional[str] = Field(None, description="区")
    address: Optional[str] = Field(None, max_length=255, description="详细地址")
    is_default: Optional[bool] = Field(None, description="是否默认地址")


class UserAddressResponse(BaseModel):
    """
    地址响应
    """
    id: int
    name: str
    phone: str
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: str
    full_address: str
    is_default: bool
    create_time: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== 刷新令牌模型 ====================

class RefreshTokenRequest(BaseModel):
    """
    刷新令牌请求
    """
    refresh_token: str = Field(..., description="刷新令牌")
