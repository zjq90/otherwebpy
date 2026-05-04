"""
会员相关数据模式
用于API请求和响应的数据验证
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class MemberLevel(str, Enum):
    """会员等级枚举"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class MemberStatus(str, Enum):
    """会员状态枚举"""
    ACTIVE = "active"
    SLEEPING = "sleeping"
    INACTIVE = "inactive"


class MemberCardBase(BaseModel):
    """会员卡基础模式"""
    card_no: str = Field(..., description="会员卡编号")
    card_type: str = Field(..., description="卡类型")
    balance: Optional[float] = Field(default=0.0, description="卡内余额")
    total_amount: Optional[float] = Field(default=0.0, description="累计充值金额")
    valid_from: date = Field(..., description="有效期开始")
    valid_to: date = Field(..., description="有效期结束")
    status: Optional[str] = Field(default="active", description="状态")


class MemberCardCreate(MemberCardBase):
    """创建会员卡模式"""
    member_id: int = Field(..., description="会员ID")


class MemberCardUpdate(BaseModel):
    """更新会员卡模式"""
    card_type: Optional[str] = None
    balance: Optional[float] = None
    total_amount: Optional[float] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    status: Optional[str] = None


class MemberCard(MemberCardBase):
    """会员卡响应模式"""
    id: int
    member_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemberBase(BaseModel):
    """会员基础模式"""
    member_no: str = Field(..., description="会员编号")
    name: str = Field(..., description="会员姓名")
    phone: str = Field(..., description="手机号码")
    email: Optional[str] = Field(default=None, description="电子邮箱")
    gender: Optional[str] = Field(default=None, description="性别")
    birthday: Optional[date] = Field(default=None, description="生日")
    address: Optional[str] = Field(default=None, description="地址")
    level: Optional[MemberLevel] = Field(default=MemberLevel.BRONZE, description="会员等级")
    status: Optional[MemberStatus] = Field(default=MemberStatus.ACTIVE, description="会员状态")


class MemberCreate(MemberBase):
    """创建会员模式"""
    pass


class MemberUpdate(BaseModel):
    """更新会员模式"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    address: Optional[str] = None
    level: Optional[MemberLevel] = None
    status: Optional[MemberStatus] = None
    total_consumption: Optional[float] = None
    points: Optional[int] = None


class Member(MemberBase):
    """会员响应模式"""
    id: int
    total_consumption: float
    points: int
    last_consumption_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    member_cards: List[MemberCard] = []

    class Config:
        from_attributes = True


class MemberListResponse(BaseModel):
    """会员列表响应模式"""
    total: int
    items: List[Member]
    page: int
    page_size: int
