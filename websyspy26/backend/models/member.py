"""
会员相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class MemberLevel(enum.Enum):
    """
    会员等级枚举
    """
    BRONZE = "bronze"      # 青铜会员
    SILVER = "silver"      # 白银会员
    GOLD = "gold"          # 黄金会员
    PLATINUM = "platinum"  # 铂金会员
    DIAMOND = "diamond"    # 钻石会员


class MemberStatus(enum.Enum):
    """
    会员状态枚举
    """
    ACTIVE = "active"        # 活跃
    SLEEPING = "sleeping"    # 沉睡（30天未消费）
    INACTIVE = "inactive"    # 不活跃


class Member(Base):
    """
    会员表模型
    存储会员基本信息
    """
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True, comment="会员ID")
    member_no = Column(String(20), unique=True, index=True, nullable=False, comment="会员编号")
    name = Column(String(50), nullable=False, comment="会员姓名")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号码")
    email = Column(String(100), comment="电子邮箱")
    gender = Column(String(10), comment="性别")
    birthday = Column(Date, comment="生日")
    address = Column(String(200), comment="地址")
    level = Column(String(20), default=MemberLevel.BRONZE.value, comment="会员等级")
    status = Column(String(20), default=MemberStatus.ACTIVE.value, comment="会员状态")
    total_consumption = Column(Float, default=0.0, comment="累计消费金额")
    points = Column(Integer, default=0, comment="积分")
    last_consumption_time = Column(DateTime, comment="最后消费时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted = Column(Integer, default=0, comment="是否删除")

    # 关联关系
    member_cards = relationship("MemberCard", back_populates="member")
    coupons = relationship("MemberCoupon", back_populates="member")
    renewal_reminders = relationship("RenewalReminder", back_populates="member")


class MemberCard(Base):
    """
    会员卡表模型
    存储会员卡信息
    """
    __tablename__ = "member_cards"

    id = Column(Integer, primary_key=True, index=True, comment="会员卡ID")
    card_no = Column(String(20), unique=True, index=True, nullable=False, comment="会员卡编号")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="关联会员ID")
    card_type = Column(String(50), nullable=False, comment="卡类型（如月卡、季卡、年卡）")
    balance = Column(Float, default=0.0, comment="卡内余额")
    total_amount = Column(Float, default=0.0, comment="累计充值金额")
    valid_from = Column(Date, nullable=False, comment="有效期开始")
    valid_to = Column(Date, nullable=False, comment="有效期结束")
    status = Column(String(20), default="active", comment="状态（active有效, expired已过期, renewed已续费）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    is_deleted = Column(Integer, default=0, comment="是否删除")

    # 关联关系
    member = relationship("Member", back_populates="member_cards")
    renewal_reminders = relationship("RenewalReminder", back_populates="member_card")
