"""
车辆模型
定义车辆表结构，用于管理运输车辆信息
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class VehicleStatus(str, enum.Enum):
    """
    车辆状态枚举
    定义车辆的当前状态
    """
    IDLE = "idle"  # 空闲：可分配任务
    IN_TRANSIT = "in_transit"  # 运输中：正在执行任务
    MAINTENANCE = "maintenance"  # 维护中：维修保养
    DISABLED = "disabled"  # 禁用：不可用


class VehicleType(str, enum.Enum):
    """
    车辆类型枚举
    定义车辆的类型
    """
    TRUCK = "truck"  # 卡车
    VAN = "van"  # 厢式货车
    TRAILER = "trailer"  # 挂车
    OTHER = "other"  # 其他


class Vehicle(Base):
    """
    车辆模型
    存储运输车辆的基本信息和实时状态
    """
    __tablename__ = "vehicles"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 车辆基本信息
    plate_number = Column(String(20), unique=True, index=True, nullable=False, comment="车牌号")
    vehicle_name = Column(String(100), nullable=False, comment="车辆名称")
    vehicle_type = Column(Enum(VehicleType), default=VehicleType.TRUCK, nullable=False, comment="车辆类型")
    
    # 车辆规格
    load_capacity = Column(Numeric(10, 2), nullable=True, comment="载重能力（吨）")
    volume = Column(Numeric(10, 2), nullable=True, comment="容积（立方米）")
    
    # 司机信息（关联用户表）
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="当前司机ID")
    
    # 状态信息
    status = Column(Enum(VehicleStatus), default=VehicleStatus.IDLE, nullable=False, comment="车辆状态")
    
    # 当前位置信息（实时更新）
    current_latitude = Column(Numeric(10, 7), nullable=True, comment="当前纬度")
    current_longitude = Column(Numeric(10, 7), nullable=True, comment="当前经度")
    current_address = Column(String(255), nullable=True, comment="当前地址")
    last_location_update = Column(DateTime, nullable=True, comment="最后位置更新时间")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 软删除标志
    is_deleted = Column(Boolean, default=False, comment="是否删除")

    # 关系定义
    # 一个车辆可以有多个运输任务
    transport_tasks = relationship("TransportTask", back_populates="vehicle")
    
    # 一个车辆可以有多个位置记录
    location_records = relationship("LocationRecord", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle(id={self.id}, plate_number={self.plate_number}, status={self.status})>"
