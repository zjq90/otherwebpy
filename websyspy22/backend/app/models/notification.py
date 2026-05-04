"""
通知相关数据模型
包含短信通知记录等
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SmsNotification(Base):
    """
    短信通知记录表
    记录发送给会员的短信通知
    """
    __tablename__ = "sms_notifications"

    id = Column(Integer, primary_key=True, index=True, comment="通知ID")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True, comment="会员ID（可为空，表示非会员通知）")
    
    # 发送信息
    phone = Column(String(20), nullable=False, comment="接收手机号")
    template_code = Column(String(50), nullable=True, comment="短信模板代码")
    template_name = Column(String(100), nullable=True, comment="短信模板名称")
    
    # 通知类型
    notification_type = Column(String(50), nullable=False, comment="通知类型: status_change/verification/consumption/reminder/other")
    title = Column(String(200), nullable=True, comment="通知标题")
    content = Column(Text, nullable=False, comment="短信内容")
    
    # 发送状态
    status = Column(String(20), default="pending", comment="发送状态: pending/sent/failed")
    error_message = Column(Text, nullable=True, comment="发送失败原因")
    sms_provider = Column(String(50), nullable=True, comment="短信服务商")
    provider_response = Column(Text, nullable=True, comment="服务商返回结果")
    
    # 重发信息
    retry_count = Column(Integer, default=0, comment="重试次数")
    last_retry_time = Column(DateTime, nullable=True, comment="最后重试时间")
    
    # 时间戳
    scheduled_time = Column(DateTime, nullable=True, comment="计划发送时间")
    sent_time = Column(DateTime, nullable=True, comment="实际发送时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系
    member = relationship("Member", back_populates="sms_notifications")
