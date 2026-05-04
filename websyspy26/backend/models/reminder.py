"""
续费提醒相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base
import enum


class ReminderType(enum.Enum):
    """
    提醒类型枚举
    """
    SEVEN_DAYS = "seven_days"    # 到期前7天
    THREE_DAYS = "three_days"    # 到期前3天


class ReminderChannel(enum.Enum):
    """
    提醒渠道枚举
    """
    SMS = "sms"          # 短信
    WECHAT = "wechat"    # 微信
    APP = "app"          # APP推送
    EMAIL = "email"      # 邮件


class ReminderStatus(enum.Enum):
    """
    提醒状态枚举
    """
    PENDING = "pending"      # 待发送
    SENT = "sent"            # 已发送
    FAILED = "failed"        # 发送失败
    RENEWED = "renewed"      # 已续费


class RenewalReminder(Base):
    """
    续费提醒记录表模型
    存储会员卡续费提醒记录
    """
    __tablename__ = "renewal_reminders"

    id = Column(Integer, primary_key=True, index=True, comment="提醒ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False, comment="会员ID")
    member_card_id = Column(Integer, ForeignKey("member_cards.id"), nullable=False, comment="会员卡ID")
    reminder_type = Column(String(20), nullable=False, comment="提醒类型")
    channel = Column(String(20), default=ReminderChannel.SMS.value, comment="提醒渠道")
    message_content = Column(String(500), comment="消息内容")
    scheduled_time = Column(DateTime, nullable=False, comment="计划发送时间")
    sent_time = Column(DateTime, comment="实际发送时间")
    status = Column(String(20), default=ReminderStatus.PENDING.value, comment="提醒状态")
    error_message = Column(String(200), comment="错误信息（发送失败时）")
    renewed_at = Column(DateTime, comment="续费时间")
    renewal_method = Column(String(20), comment="续费方式（offline到店, online线上）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联关系
    member = relationship("Member", back_populates="renewal_reminders")
    member_card = relationship("MemberCard", back_populates="renewal_reminders")
