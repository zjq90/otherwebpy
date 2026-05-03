"""
通知Pydantic模型
用于通知相关API的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    """
    通知基础模型
    """
    user_id: Optional[int] = Field(None, description="接收者ID")
    reservation_id: Optional[int] = Field(None, description="关联预约ID")
    notification_type: str = Field(..., description="通知类型")
    title: str = Field(..., max_length=200, description="通知标题")
    content: Optional[str] = Field(None, description="通知内容")


class NotificationCreate(NotificationBase):
    """
    通知创建模型
    """
    pass


class NotificationResponse(NotificationBase):
    """
    通知响应模型
    """
    id: int
    status: str
    sms_sent: bool
    sms_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    reservation_no: Optional[str] = None

    class Config:
        from_attributes = True
