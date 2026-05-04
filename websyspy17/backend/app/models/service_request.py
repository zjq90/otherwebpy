from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ServiceType(str, enum.Enum):
    """
    服务类型枚举
    """
    REPAIR = "repair"
    COMPLAINT = "complaint"
    CONSULT = "consult"


class ServiceStatus(str, enum.Enum):
    """
    服务状态枚举
    """
    PENDING = "pending"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CLOSED = "closed"


class ServiceRequest(Base):
    """
    服务请求模型
    存储业主提交的报修、投诉、咨询等服务请求
    """
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True, comment="服务请求ID")
    title = Column(String(200), nullable=False, comment="请求标题")
    description = Column(Text, comment="请求描述详情")
    service_type = Column(String(20), nullable=False, comment="服务类型：repair/complaint/consult")
    status = Column(String(20), default=ServiceStatus.PENDING.value, comment="状态：pending/assigned/processing/completed/closed")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="提交用户ID")
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="处理人ID")
    
    room_number = Column(String(20), comment="房间号/门牌号")
    contact_name = Column(String(50), comment="联系人姓名")
    contact_phone = Column(String(20), comment="联系电话")
    
    priority = Column(Integer, default=1, comment="优先级：1-普通，2-紧急，3-非常紧急")
    location = Column(String(100), comment="具体位置描述")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    submitter = relationship("User", foreign_keys=[user_id], backref="submitted_requests")
    assignee = relationship("User", foreign_keys=[assignee_id], backref="assigned_requests")

    def __repr__(self):
        return f"<ServiceRequest(id={self.id}, title={self.title}, status={self.status})>"


class ServiceProgress(Base):
    """
    服务进度记录模型
    记录服务请求处理过程中的每一步操作
    """
    __tablename__ = "service_progress"

    id = Column(Integer, primary_key=True, index=True, comment="进度记录ID")
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False, comment="服务请求ID")
    
    action = Column(String(50), nullable=False, comment="操作类型")
    description = Column(Text, comment="进度描述")
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="操作人ID")
    
    from_status = Column(String(20), comment="变更前状态")
    to_status = Column(String(20), comment="变更后状态")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<ServiceProgress(id={self.id}, action={self.action})>"
