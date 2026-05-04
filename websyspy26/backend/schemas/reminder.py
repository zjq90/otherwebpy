"""
续费提醒相关数据模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class ReminderType(str, Enum):
    """提醒类型枚举"""
    SEVEN_DAYS = "seven_days"
    THREE_DAYS = "three_days"


class ReminderChannel(str, Enum):
    """提醒渠道枚举"""
    SMS = "sms"
    WECHAT = "wechat"
    APP = "app"
    EMAIL = "email"


class ReminderStatus(str, Enum):
    """提醒状态枚举"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RENEWED = "renewed"


class RenewalReminderBase(BaseModel):
    """续费提醒基础模式"""
    reminder_type: ReminderType = Field(..., description="提醒类型")
    channel: Optional[ReminderChannel] = Field(default=ReminderChannel.SMS, description="提醒渠道")
    message_content: Optional[str] = Field(default=None, description="消息内容")
    scheduled_time: datetime = Field(..., description="计划发送时间")
    status: Optional[ReminderStatus] = Field(default=ReminderStatus.PENDING, description="提醒状态")


class RenewalReminderCreate(RenewalReminderBase):
    """创建续费提醒模式"""
    member_id: int = Field(..., description="会员ID")
    member_card_id: int = Field(..., description="会员卡ID")


class RenewalReminderUpdate(BaseModel):
    """更新续费提醒模式"""
    channel: Optional[ReminderChannel] = None
    message_content: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    sent_time: Optional[datetime] = None
    status: Optional[ReminderStatus] = None
    error_message: Optional[str] = None
    renewed_at: Optional[datetime] = None
    renewal_method: Optional[str] = None


class RenewalReminder(RenewalReminderBase):
    """续费提醒响应模式"""
    id: int
    member_id: int
    member_card_id: int
    sent_time: Optional[datetime]
    error_message: Optional[str]
    renewed_at: Optional[datetime]
    renewal_method: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RenewalReminderListResponse(BaseModel):
    """续费提醒列表响应模式"""
    total: int
    items: List[RenewalReminder]
    page: int
    page_size: int
