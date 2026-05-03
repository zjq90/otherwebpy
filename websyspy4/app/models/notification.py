"""
通知模型
定义消息通知表结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    """
    通知类型枚举
    NEW_RESERVATION: 新预约
    DEPOSIT_PAID: 押金已支付
    RESERVATION_CONFIRMED: 预约已确认
    PICKUP_REMINDER: 领取提醒
    RETURN_REMINDER: 归还提醒
    SYSTEM: 系统通知
    """
    NEW_RESERVATION = "new_reservation"
    DEPOSIT_PAID = "deposit_paid"
    RESERVATION_CONFIRMED = "reservation_confirmed"
    PICKUP_REMINDER = "pickup_reminder"
    RETURN_REMINDER = "return_reminder"
    SYSTEM = "system"


class NotificationStatus(str, enum.Enum):
    """
    通知状态枚举
    UNREAD: 未读
    READ: 已读
    """
    UNREAD = "unread"
    READ = "read"


class Notification(Base):
    """
    通知模型类
    对应数据库中的notifications表
    """
    __tablename__ = "notifications"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="通知ID")
    
    # 接收者用户ID（外键），NULL表示所有管理员
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="接收者ID")
    
    # 关联的预约ID（外键）
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True, comment="关联预约ID")
    
    # 通知类型
    notification_type = Column(String(50), nullable=False, comment="通知类型")
    
    # 通知标题
    title = Column(String(200), nullable=False, comment="通知标题")
    
    # 通知内容
    content = Column(Text, nullable=True, comment="通知内容")
    
    # 通知状态
    status = Column(String(20), default=NotificationStatus.UNREAD, comment="通知状态")
    
    # 短信发送状态
    sms_sent = Column(Boolean, default=False, comment="短信是否已发送")
    
    # 短信发送时间
    sms_sent_at = Column(DateTime, nullable=True, comment="短信发送时间")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 读取时间
    read_at = Column(DateTime, nullable=True, comment="读取时间")
    
    # 关联用户
    user = relationship("User")
    
    # 关联预约
    reservation = relationship("Reservation")

    def to_dict(self):
        """
        将通知对象转换为字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "reservation_id": self.reservation_id,
            "notification_type": self.notification_type,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "sms_sent": self.sms_sent,
            "sms_sent_at": self.sms_sent_at.isoformat() if self.sms_sent_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "reservation_no": self.reservation.reservation_no if self.reservation else None
        }
