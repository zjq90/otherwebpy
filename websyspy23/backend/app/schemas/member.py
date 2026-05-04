"""
会员管理Pydantic Schema
定义会员、会员卡和课程预约的请求/响应数据模型
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date


class MemberBase(BaseModel):
    """
    会员基础Schema
    包含会员的基本字段
    """
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    phone: str = Field(..., min_length=1, max_length=20, description="手机号码")
    email: Optional[EmailStr] = Field(None, max_length=100, description="邮箱")
    birthday: Optional[date] = Field(None, description="出生日期")
    id_card: Optional[str] = Field(None, max_length=50, description="身份证号")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    emergency_contact: Optional[str] = Field(None, max_length=100, description="紧急联系人")
    emergency_phone: Optional[str] = Field(None, max_length=20, description="紧急联系电话")
    health_status: Optional[str] = Field(None, description="健康状况")
    remarks: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field("active", max_length=20, description="会员状态")


class MemberCreate(MemberBase):
    """
    会员创建Schema
    继承自MemberBase，用于创建新的会员
    """
    pass


class MemberUpdate(BaseModel):
    """
    会员更新Schema
    所有字段都是可选的，用于部分更新
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="姓名")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    phone: Optional[str] = Field(None, min_length=1, max_length=20, description="手机号码")
    email: Optional[EmailStr] = Field(None, max_length=100, description="邮箱")
    birthday: Optional[date] = Field(None, description="出生日期")
    id_card: Optional[str] = Field(None, max_length=50, description="身份证号")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")
    emergency_contact: Optional[str] = Field(None, max_length=100, description="紧急联系人")
    emergency_phone: Optional[str] = Field(None, max_length=20, description="紧急联系电话")
    health_status: Optional[str] = Field(None, description="健康状况")
    remarks: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="会员状态")


class MemberResponse(MemberBase):
    """
    会员响应Schema
    包含会员的所有字段，用于返回给前端
    """
    id: int = Field(..., description="会员ID")
    member_no: str = Field(..., description="会员编号")
    register_time: datetime = Field(..., description="注册时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class MemberCardBase(BaseModel):
    """
    会员卡基础Schema
    包含会员卡的基本字段
    """
    member_id: int = Field(..., description="会员ID")
    card_id: int = Field(..., description="卡项ID")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    total_count: Optional[int] = Field(None, ge=0, description="总次数")
    remaining_count: Optional[int] = Field(None, ge=0, description="剩余次数")
    balance: Optional[float] = Field(0, ge=0, description="储值余额")
    bonus_balance: Optional[float] = Field(0, ge=0, description="赠送余额")
    purchase_price: Optional[float] = Field(None, gt=0, description="购买价格")
    status: Optional[str] = Field("active", max_length=20, description="会员卡状态")
    remarks: Optional[str] = Field(None, description="备注")


class MemberCardCreate(MemberCardBase):
    """
    会员卡创建Schema
    继承自MemberCardBase，用于创建新的会员卡
    """
    pass


class MemberCardUpdate(BaseModel):
    """
    会员卡更新Schema
    所有字段都是可选的，用于部分更新
    """
    member_id: Optional[int] = Field(None, description="会员ID")
    card_id: Optional[int] = Field(None, description="卡项ID")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    total_count: Optional[int] = Field(None, ge=0, description="总次数")
    remaining_count: Optional[int] = Field(None, ge=0, description="剩余次数")
    balance: Optional[float] = Field(None, ge=0, description="储值余额")
    bonus_balance: Optional[float] = Field(None, ge=0, description="赠送余额")
    purchase_price: Optional[float] = Field(None, gt=0, description="购买价格")
    status: Optional[str] = Field(None, max_length=20, description="会员卡状态")
    remarks: Optional[str] = Field(None, description="备注")


class MemberCardResponse(MemberCardBase):
    """
    会员卡响应Schema
    包含会员卡的所有字段，用于返回给前端
    """
    id: int = Field(..., description="会员卡ID")
    card_no: str = Field(..., description="会员卡编号")
    activate_time: datetime = Field(..., description="激活时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    card_name: Optional[str] = Field(None, description="卡项名称")
    card_type_name: Optional[str] = Field(None, description="卡类型名称")
    
    class Config:
        from_attributes = True


class CourseBookingBase(BaseModel):
    """
    课程预约基础Schema
    包含课程预约的基本字段
    """
    member_id: int = Field(..., description="会员ID")
    schedule_id: int = Field(..., description="排期ID")
    status: Optional[str] = Field("booked", max_length=20, description="预约状态")
    remarks: Optional[str] = Field(None, description="备注")


class CourseBookingCreate(CourseBookingBase):
    """
    课程预约创建Schema
    继承自CourseBookingBase，用于创建新的课程预约
    """
    pass


class CourseBookingUpdate(BaseModel):
    """
    课程预约更新Schema
    所有字段都是可选的，用于部分更新
    """
    member_id: Optional[int] = Field(None, description="会员ID")
    schedule_id: Optional[int] = Field(None, description="排期ID")
    status: Optional[str] = Field(None, max_length=20, description="预约状态")
    check_in_time: Optional[datetime] = Field(None, description="签到时间")
    cancel_time: Optional[datetime] = Field(None, description="取消时间")
    cancel_reason: Optional[str] = Field(None, description="取消原因")
    remarks: Optional[str] = Field(None, description="备注")


class CourseBookingResponse(CourseBookingBase):
    """
    课程预约响应Schema
    包含课程预约的所有字段，用于返回给前端
    """
    id: int = Field(..., description="预约ID")
    booking_no: str = Field(..., description="预约编号")
    check_in_time: Optional[datetime] = Field(None, description="签到时间")
    cancel_time: Optional[datetime] = Field(None, description="取消时间")
    cancel_reason: Optional[str] = Field(None, description="取消原因")
    booking_time: datetime = Field(..., description="预约时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    member: Optional[MemberResponse] = Field(None, description="关联的会员")
    
    class Config:
        from_attributes = True
