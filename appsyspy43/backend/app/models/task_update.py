"""
任务更新模型
定义任务更新记录表结构，用于记录运输任务的状态变更历史
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.transport_task import TaskStatus


class TaskUpdate(Base):
    """
    任务更新模型
    存储运输任务的状态变更记录，包括状态变更、操作人、时间和备注等信息
    """
    __tablename__ = "task_updates"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联信息
    transport_task_id = Column(Integer, ForeignKey("transport_tasks.id"), nullable=False, index=True, comment="任务ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="操作人ID")
    
    # 状态信息
    old_status = Column(Enum(TaskStatus), nullable=True, comment="变更前状态")
    new_status = Column(Enum(TaskStatus), nullable=False, comment="变更后状态")
    
    # 更新信息
    update_type = Column(String(50), nullable=False, comment="更新类型（如：状态变更、分配任务、上传照片等）")
    description = Column(Text, nullable=True, comment="更新描述")
    
    # 照片信息（用于卸料照片等）
    photo_paths = Column(Text, nullable=True, comment="照片路径（多个用逗号分隔）")
    
    # 位置信息（可选，记录操作时的位置）
    latitude = Column(String(20), nullable=True, comment="操作时纬度")
    longitude = Column(String(20), nullable=True, comment="操作时经度")
    address = Column(String(500), nullable=True, comment="操作时地址")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系定义
    # 一个任务更新属于一个运输任务
    transport_task = relationship("TransportTask", back_populates="task_updates")
    
    # 一个任务更新属于一个用户（操作人）
    user = relationship("User", back_populates="task_updates")

    def __repr__(self):
        return f"<TaskUpdate(id={self.id}, task_id={self.transport_task_id}, new_status={self.new_status})>"
