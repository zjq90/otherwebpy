"""
位置记录模型
定义位置记录表结构，用于存储车辆的实时位置和行驶轨迹
"""

from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class LocationRecord(Base):
    """
    位置记录模型
    存储车辆和司机的位置信息，用于实时监控和轨迹回放
    """
    __tablename__ = "location_records"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联信息
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True, comment="车辆ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="司机用户ID")
    transport_task_id = Column(Integer, ForeignKey("transport_tasks.id"), nullable=True, index=True, comment="关联任务ID")
    
    # 位置信息
    latitude = Column(Numeric(10, 7), nullable=False, comment="纬度")
    longitude = Column(Numeric(10, 7), nullable=False, comment="经度")
    address = Column(String(500), nullable=True, comment="地址描述")
    
    # 附加信息
    speed = Column(Numeric(10, 2), nullable=True, comment="速度（km/h）")
    direction = Column(Numeric(5, 2), nullable=True, comment="方向（角度，0-360）")
    accuracy = Column(Numeric(10, 2), nullable=True, comment="定位精度（米）")
    
    # 设备信息
    device_type = Column(String(50), nullable=True, comment="设备类型（如：GPS、手机）")
    device_id = Column(String(100), nullable=True, comment="设备唯一标识")
    
    # 时间戳
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True, comment="记录时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 关系定义
    # 一个位置记录属于一个车辆
    vehicle = relationship("Vehicle", back_populates="location_records")
    
    # 一个位置记录属于一个用户（司机）
    user = relationship("User", back_populates="location_records")

    # 创建复合索引，提高按时间和车辆查询的性能
    __table_args__ = (
        Index('idx_vehicle_time', 'vehicle_id', 'recorded_at'),
        Index('idx_task_time', 'transport_task_id', 'recorded_at'),
    )

    def __repr__(self):
        return f"<LocationRecord(id={self.id}, vehicle_id={self.vehicle_id}, recorded_at={self.recorded_at})>"
