"""
促销活动相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class PromotionType(enum.Enum):
    """
    促销活动类型枚举
    """
    DISCOUNT = "discount"        # 限时折扣
    FULL_REDUCTION = "full_reduction"  # 满减券
    EXPERIENCE = "experience"    # 体验券


class PromotionStatus(enum.Enum):
    """
    促销活动状态枚举
    """
    DRAFT = "draft"          # 草稿
    ACTIVE = "active"        # 进行中
    ENDED = "ended"          # 已结束
    CANCELLED = "cancelled"  # 已取消


class TargetType(enum.Enum):
    """
    目标用户类型枚举
    """
    ALL = "all"                  # 全部会员
    SLEEPING = "sleeping"        # 沉睡会员
    HIGH_VALUE = "high_value"    # 高价值客户
    SPECIFIC = "specific"        # 指定会员


class Promotion(Base):
    """
    促销活动表模型
    存储促销活动基本信息
    """
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, comment="活动ID")
    name = Column(String(100), nullable=False, comment="活动名称")
    type = Column(String(20), nullable=False, comment="活动类型")
    description = Column(String(500), comment="活动描述")
    discount_rate = Column(Float, comment="折扣率（0-1之间，如0.8表示8折）")
    full_amount = Column(Float, comment="满减条件金额")
    reduction_amount = Column(Float, comment="减免金额")
    experience_amount = Column(Float, comment="体验券金额")
    valid_from = Column(DateTime, nullable=False, comment="活动开始时间")
    valid_to = Column(DateTime, nullable=False, comment="活动结束时间")
    total_quantity = Column(Integer, default=1, comment="发放总量")
    used_quantity = Column(Integer, default=0, comment="已使用数量")
    per_member_limit = Column(Integer, default=1, comment="每人限领数量")
    target_type = Column(String(20), default=TargetType.ALL.value, comment="目标用户类型")
    target_member_ids = Column(String(1000), comment="指定会员ID列表（JSON格式）")
    status = Column(String(20), default=PromotionStatus.DRAFT.value, comment="活动状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted = Column(Integer, default=0, comment="是否删除")

    # 关联关系
    coupons = relationship("Coupon", back_populates="promotion")


class CouponStatus(enum.Enum):
    """
    优惠券状态枚举
    """
    AVAILABLE = "available"    # 可用
    CLAIMED = "claimed"        # 已领取
    USED = "used"              # 已使用
    EXPIRED = "expired"        # 已过期


class Coupon(Base):
    """
    优惠券表模型
    存储优惠券信息
    """
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, comment="优惠券ID")
    coupon_no = Column(String(30), unique=True, index=True, nullable=False, comment="优惠券编号")
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=False, comment="关联活动ID")
    type = Column(String(20), nullable=False, comment="优惠券类型")
    name = Column(String(100), nullable=False, comment="优惠券名称")
    discount_rate = Column(Float, comment="折扣率")
    full_amount = Column(Float, comment="满减条件金额")
    reduction_amount = Column(Float, comment="减免金额")
    experience_amount = Column(Float, comment="体验券金额")
    valid_from = Column(DateTime, nullable=False, comment="有效期开始")
    valid_to = Column(DateTime, nullable=False, comment="有效期结束")
    status = Column(String(20), default=CouponStatus.AVAILABLE.value, comment="优惠券状态")
    claimed_at = Column(DateTime, comment="领取时间")
    used_at = Column(DateTime, comment="使用时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    promotion = relationship("Promotion", back_populates="coupons")
    member_coupons = relationship("MemberCoupon", back_populates="coupon")


class MemberCoupon(Base):
    """
    会员优惠券关联表模型
    存储会员领取的优惠券
    """
    __tablename__ = "member_coupons"

    id = Column(Integer, primary_key=True, index=True, comment="关联ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False, comment="优惠券ID")
    status = Column(String(20), default="claimed", comment="状态（claimed已领取, used已使用, expired已过期）")
    claimed_at = Column(DateTime, default=datetime.now, comment="领取时间")
    used_at = Column(DateTime, comment="使用时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    member = relationship("Member", back_populates="coupons")
    coupon = relationship("Coupon", back_populates="member_coupons")
