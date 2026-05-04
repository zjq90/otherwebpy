"""
会员相关Pydantic模型
定义会员的请求和响应数据格式
"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from app.models.member import MemberStatus, RegistrationChannel, VerificationMethod


class MemberBase(BaseModel):
    """
    会员基础模型
    包含会员的基本字段
    """
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    id_card: Optional[str] = Field(default=None, max_length=18, description="身份证号")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别")
    birth_date: Optional[date] = Field(default=None, description="出生日期")
    address: Optional[str] = Field(default=None, max_length=500, description="联系地址")
    
    # 健康状况
    health_status: Optional[str] = Field(default=None, max_length=1000, description="健康状况描述")
    allergies: Optional[str] = Field(default=None, max_length=500, description="过敏史")
    emergency_contact: Optional[str] = Field(default=None, max_length=100, description="紧急联系人")
    emergency_phone: Optional[str] = Field(default=None, max_length=20, description="紧急联系电话")
    
    class Config:
        from_attributes = True


class MemberCreate(MemberBase):
    """
    会员创建模型
    用于新增会员时的请求数据
    """
    registration_channel: RegistrationChannel = Field(
        default=RegistrationChannel.OFFLINE,
        description="注册渠道"
    )
    verification_method: Optional[VerificationMethod] = Field(
        default=None,
        description="实名认证方式"
    )
    
    @validator('phone')
    def validate_phone(cls, v):
        """
        验证手机号格式
        """
        if not v.isdigit():
            raise ValueError('手机号必须为数字')
        if len(v) != 11:
            raise ValueError('手机号必须为11位')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "张三",
                "phone": "13800138000",
                "id_card": "110101199001011234",
                "email": "zhangsan@example.com",
                "gender": "男",
                "birth_date": "1990-01-01",
                "address": "北京市朝阳区",
                "health_status": "健康状况良好，无重大疾病史",
                "allergies": "青霉素过敏",
                "emergency_contact": "李四",
                "emergency_phone": "13900139000",
                "registration_channel": "offline",
                "verification_method": "phone"
            }
        }


class MemberUpdate(BaseModel):
    """
    会员更新模型
    用于修改会员信息时的请求数据
    所有字段都是可选的
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="姓名")
    phone: Optional[str] = Field(default=None, min_length=11, max_length=20, description="手机号")
    id_card: Optional[str] = Field(default=None, max_length=18, description="身份证号")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    gender: Optional[str] = Field(default=None, max_length=10, description="性别")
    birth_date: Optional[date] = Field(default=None, description="出生日期")
    address: Optional[str] = Field(default=None, max_length=500, description="联系地址")
    health_status: Optional[str] = Field(default=None, max_length=1000, description="健康状况描述")
    allergies: Optional[str] = Field(default=None, max_length=500, description="过敏史")
    emergency_contact: Optional[str] = Field(default=None, max_length=100, description="紧急联系人")
    emergency_phone: Optional[str] = Field(default=None, max_length=20, description="紧急联系电话")
    
    class Config:
        from_attributes = True


class MemberResponse(MemberBase):
    """
    会员响应模型
    用于返回会员详情信息
    """
    id: int = Field(description="会员ID")
    registration_channel: RegistrationChannel = Field(description="注册渠道")
    verification_method: Optional[VerificationMethod] = Field(description="实名认证方式")
    is_verified: int = Field(description="是否已实名认证: 0-否, 1-是")
    current_level: str = Field(description="当前会员等级")
    total_consumption: int = Field(description="累计消费金额（分）")
    total_visits: int = Field(description="累计到店次数")
    status: MemberStatus = Field(description="账户状态")
    status_reason: Optional[str] = Field(description="状态变更原因")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """
    会员列表项响应模型
    用于会员列表展示的简化信息
    """
    id: int = Field(description="会员ID")
    name: str = Field(description="姓名")
    phone: str = Field(description="手机号")
    gender: Optional[str] = Field(description="性别")
    current_level: str = Field(description="当前会员等级")
    total_consumption: int = Field(description="累计消费金额（分）")
    status: MemberStatus = Field(description="账户状态")
    is_verified: int = Field(description="是否已实名认证")
    created_at: datetime = Field(description="注册时间")
    
    class Config:
        from_attributes = True


class VerificationRequest(BaseModel):
    """
    实名认证请求模型
    用于会员实名认证的请求数据
    """
    verification_method: VerificationMethod = Field(description="实名认证方式")
    verification_code: Optional[str] = Field(default=None, description="验证码（手机号验证时使用）")
    face_image_data: Optional[str] = Field(default=None, description="人脸图像数据（人脸识别时使用，base64编码）")
    
    class Config:
        schema_extra = {
            "example": {
                "verification_method": "phone",
                "verification_code": "123456"
            }
        }


class StatusChangeReason(BaseModel):
    """
    简单状态变更请求模型
    用于专门的冻结、解冻、注销端点
    """
    reason: Optional[str] = Field(default=None, max_length=500, description="变更原因")
    operator: Optional[str] = Field(default=None, max_length=100, description="操作人")
    
    class Config:
        schema_extra = {
            "example": {
                "reason": "账户异常，需临时冻结",
                "operator": "管理员"
            }
        }


class StatusChangeRequest(StatusChangeReason):
    """
    完整状态变更请求模型
    用于通用的状态变更接口
    """
    new_status: MemberStatus = Field(description="新状态")
    
    class Config:
        schema_extra = {
            "example": {
                "new_status": "frozen",
                "reason": "账户异常，需临时冻结",
                "operator": "管理员"
            }
        }


class PhoneVerificationCodeRequest(BaseModel):
    """
    手机验证码发送请求模型
    """
    phone: str = Field(..., min_length=11, max_length=20, description="手机号")
    purpose: str = Field(default="verification", description="验证码用途：verification-实名认证, login-登录")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit():
            raise ValueError('手机号必须为数字')
        if len(v) != 11:
            raise ValueError('手机号必须为11位')
        return v
