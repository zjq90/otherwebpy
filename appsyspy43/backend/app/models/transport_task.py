"""
运输任务模型
定义运输任务表结构，用于管理运输任务的全生命周期
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class TaskStatus(str, enum.Enum):
    """
    任务状态枚举
    定义运输任务的生命周期状态
    """
    PENDING = "pending"  # 待分配：已创建但未分配给司机
    ASSIGNED = "assigned"  # 已分配：已分配给司机，等待司机确认
    CONFIRMED = "confirmed"  # 已确认：司机已确认接受任务
    DEPARTED = "departed"  # 已出发：司机已出发
    ARRIVED = "arrived"  # 已到达：已到达目的地
    UNLOADING = "unloading"  # 卸料中：正在卸料
    COMPLETED = "completed"  # 已完成：任务完成
    CANCELLED = "cancelled"  # 已取消：任务被取消


class TransportTask(Base):
    """
    运输任务模型
    存储运输任务的完整信息，包括任务详情、地点信息、时间安排等
    """
    __tablename__ = "transport_tasks"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 任务编号（自动生成，方便管理）
    task_no = Column(String(50), unique=True, index=True, nullable=False, comment="任务编号")
    
    # 任务基本信息
    task_name = Column(String(200), nullable=False, comment="任务名称")
    task_description = Column(Text, nullable=True, comment="任务描述")
    
    # 货物信息
    cargo_name = Column(String(200), nullable=False, comment="货物名称")
    cargo_weight = Column(Numeric(10, 2), nullable=True, comment="货物重量（吨）")
    cargo_volume = Column(Numeric(10, 2), nullable=True, comment="货物体积（立方米）")
    cargo_quantity = Column(Integer, nullable=True, comment="货物数量")
    
    # 装货地点信息
    loading_address = Column(String(500), nullable=False, comment="装货地址")
    loading_latitude = Column(Numeric(10, 7), nullable=True, comment="装货纬度")
    loading_longitude = Column(Numeric(10, 7), nullable=True, comment="装货经度")
    loading_contact = Column(String(50), nullable=True, comment="装货联系人")
    loading_phone = Column(String(20), nullable=True, comment="装货联系电话")
    
    # 卸货地点信息
    unloading_address = Column(String(500), nullable=False, comment="卸货地址")
    unloading_latitude = Column(Numeric(10, 7), nullable=True, comment="卸货纬度")
    unloading_longitude = Column(Numeric(10, 7), nullable=True, comment="卸货经度")
    unloading_contact = Column(String(50), nullable=False, comment="卸货联系人")
    unloading_phone = Column(String(20), nullable=False, comment="卸货联系电话")
    
    # 时间安排
    scheduled_departure_time = Column(DateTime, nullable=True, comment="计划出发时间")
    scheduled_arrival_time = Column(DateTime, nullable=True, comment="计划到达时间")
    estimated_arrival_time = Column(DateTime, nullable=True, comment="预计到达时间（实时更新）")
    
    # 实际时间
    actual_departure_time = Column(DateTime, nullable=True, comment="实际出发时间")
    actual_arrival_time = Column(DateTime, nullable=True, comment="实际到达时间")
    actual_unload_time = Column(DateTime, nullable=True, comment="实际卸料时间")
    completed_time = Column(DateTime, nullable=True, comment="完成时间")
    
    # 卸料照片（存储文件路径，多个用逗号分隔）
    unload_photos = Column(Text, nullable=True, comment="卸料照片路径")
    
    # 备注信息
    remarks = Column(Text, nullable=True, comment="备注信息")
    
    # 关联信息
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True, comment="车辆ID")
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="司机ID")
    dispatcher_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="调度员ID")
    
    # 状态信息
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, comment="任务状态")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 软删除标志
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    # 关系定义
    # 一个任务属于一个车辆
    vehicle = relationship("Vehicle", back_populates="transport_tasks", foreign_keys=[vehicle_id])
    
    # 一个任务属于一个司机
    driver = relationship("User", back_populates="transport_tasks", foreign_keys=[driver_id])
    
    # 一个任务由一个调度员分配
    dispatcher = relationship("User", back_populates="assigned_tasks", foreign_keys=[dispatcher_id])
    
    # 一个任务可以有多个状态更新记录
    task_updates = relationship("TaskUpdate", back_populates="transport_task")

    def __repr__(self):
        return f"<TransportTask(id={self.id}, task_no={self.task_no}, status={self.status})>"
