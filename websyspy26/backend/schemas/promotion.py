"""
促销活动相关数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PromotionType(str, Enum):
    """促销活动类型枚举"""
    DISCOUNT = "discount"
    FULL_REDUCTION = "full_reduction"
    EXPERIENCE = "experience"


class PromotionStatus(str, Enum):
    """促销活动状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class TargetType(str, Enum):
    """目标用户类型枚举"""
    ALL = "all"
    SLEEPING = "sleeping"
    HIGH_VALUE = "high_value"
    SPECIFIC = "specific"


class CouponStatus(str, Enum):
    """优惠券状态枚举"""
    AVAILABLE = "available"
    CLAIMED = "claimed"
    USED = "used"
    EXPIRED = "expired"


class CouponBase(BaseModel):
    """优惠券基础模式"""
    coupon_no: str = Field(..., description="优惠券编号")
    type: str = Field(..., description="优惠券类型")
    name: str = Field(..., description="优惠券名称")
    discount_rate: Optional[float] = Field(default=None, description="折扣率")
    full_amount: Optional[float] = Field(default=None, description="满减条件金额")
    reduction_amount: Optional[float] = Field(default=None, description="减免金额")
    experience_amount: Optional[float] = Field(default=None, description="体验券金额")
    valid_from: datetime = Field(..., description="有效期开始")
    valid_to: datetime = Field(..., description="有效期结束")
    status: Optional[str] = Field(default=CouponStatus.AVAILABLE, description="状态")


class CouponCreate(CouponBase):
    """创建优惠券模式"""
    promotion_id: int = Field(..., description="活动ID")


class Coupon(CouponBase):
    """优惠券响应模式"""
    id: int
    promotion_id: int
    claimed_at: Optional[datetime]
    used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromotionBase(BaseModel):
    """促销活动基础模式"""
    name: str = Field(..., description="活动名称")
    type: PromotionType = Field(..., description="活动类型")
    description: Optional[str] = Field(default=None, description="活动描述")
    discount_rate: Optional[float] = Field(default=None, description="折扣率")
    full_amount: Optional[float] = Field(default=None, description="满减条件金额")
    reduction_amount: Optional[float] = Field(default=None, description="减免金额")
    experience_amount: Optional[float] = Field(default=None, description="体验券金额")
    valid_from: datetime = Field(..., description="活动开始时间")
    valid_to: datetime = Field(..., description="活动结束时间")
    total_quantity: Optional[int] = Field(default=1, description="发放总量")
    per_member_limit: Optional[int] = Field(default=1, description="每人限领数量")
    target_type: Optional[TargetType] = Field(default=TargetType.ALL, description="目标用户类型")
    target_member_ids: Optional[str] = Field(default=None, description="指定会员ID列表")
    status: Optional[PromotionStatus] = Field(default=PromotionStatus.DRAFT, description="活动状态")


class PromotionCreate(PromotionBase):
    """创建促销活动模式"""
    pass


class PromotionUpdate(BaseModel):
    """更新促销活动模式"""
    name: Optional[str] = None
    type: Optional[PromotionType] = None
    description: Optional[str] = None
    discount_rate: Optional[float] = None
    full_amount: Optional[float] = None
    reduction_amount: Optional[float] = None
    experience_amount: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    total_quantity: Optional[int] = None
    per_member_limit: Optional[int] = None
    target_type: Optional[TargetType] = None
    target_member_ids: Optional[str] = None
    status: Optional[PromotionStatus] = None


class Promotion(PromotionBase):
    """促销活动响应模式"""
    id: int
    used_quantity: int
    created_at: datetime
    updated_at: datetime
    coupons: List[Coupon] = []

    class Config:
        from_attributes = True


class PromotionListResponse(BaseModel):
    """促销活动列表响应模式"""
    total: int
    items: List[Promotion]
    page: int
    page_size: int


class MemberCouponBase(BaseModel):
    """会员优惠券关联基础模式"""
    status: Optional[str] = Field(default="claimed", description="状态")


class MemberCouponCreate(MemberCouponBase):
    """创建会员优惠券关联模式"""
    member_id: int = Field(..., description="会员ID")
    coupon_id: int = Field(..., description="优惠券ID")


class MemberCoupon(MemberCouponBase):
    """会员优惠券关联响应模式"""
    id: int
    member_id: int
    coupon_id: int
    claimed_at: datetime
    used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
