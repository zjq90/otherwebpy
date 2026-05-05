from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class SensorData(Base):
    """
    传感器数据表
    存储传感器实时采集的数据，包括电流、温度、振动等
    """
    
    __tablename__ = "sensor_data"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的传感器ID
    sensor_id = Column(Integer, ForeignKey("sensor.id"), nullable=False, index=True, comment="关联传感器ID")
    
    # 采集数值
    value = Column(Float, nullable=False, comment="采集数值")
    
    # 数据状态：正常、预警、报警
    status = Column(String(20), default="正常", comment="数据状态")
    
    # 是否为异常数据
    is_abnormal = Column(Boolean, default=False, comment="是否异常")
    
    # 采集时间
    collected_at = Column(DateTime, default=datetime.now, index=True, comment="采集时间")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 关系：关联传感器
    sensor = relationship("Sensor", back_populates="sensor_data")


class OperationLog(Base):
    """
    设备运行日志表
    记录设备的运行状态变更、故障事件等数字化运行日志
    """
    
    __tablename__ = "operation_log"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的设备ID
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True, comment="关联设备ID")
    
    # 日志类型：运行状态变更、故障事件、维护记录等
    log_type = Column(String(50), nullable=False, comment="日志类型")
    
    # 日志级别：信息、警告、错误、严重
    level = Column(String(20), default="信息", comment="日志级别")
    
    # 日志标题
    title = Column(String(200), nullable=False, comment="日志标题")
    
    # 日志内容
    content = Column(Text, comment="日志内容")
    
    # 原始状态
    from_status = Column(String(50), comment="原始状态")
    
    # 目标状态
    to_status = Column(String(50), comment="目标状态")
    
    # 关联的传感器数据ID（可选）
    related_sensor_data_id = Column(Integer, comment="关联传感器数据ID")
    
    # 记录时间
    recorded_at = Column(DateTime, default=datetime.now, index=True, comment="记录时间")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 关系：关联设备
    equipment = relationship("Equipment", back_populates="operation_logs")


class ControlSystemStatus(Base):
    """
    控制系统监控表
    监控电力控制系统的状态，包括断电保护、数据隔离、抗干扰能力等
    """
    
    __tablename__ = "control_system_status"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 监控项名称
    monitor_item = Column(String(100), nullable=False, comment="监控项名称")
    
    # 监控项类型：断电保护、数据隔离、抗干扰能力、电压稳定等
    monitor_type = Column(String(50), nullable=False, index=True, comment="监控项类型")
    
    # 当前状态值
    current_value = Column(String(200), comment="当前状态值")
    
    # 数值类型的值（如果适用）
    numeric_value = Column(Float, comment="数值类型值")
    
    # 单位（如：V、A、ms）
    unit = Column(String(20), comment="单位")
    
    # 正常状态描述
    normal_status = Column(String(200), comment="正常状态描述")
    
    # 当前状态：正常、异常、预警、故障
    status = Column(String(20), default="正常", comment="当前状态")
    
    # 是否启用
    is_enabled = Column(Boolean, default=True, comment="是否启用")
    
    # 最后检查时间
    last_checked_at = Column(DateTime, default=datetime.now, comment="最后检查时间")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
