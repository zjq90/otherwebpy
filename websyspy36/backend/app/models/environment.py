"""
环保合规监管模块的数据库模型
包含粉尘监测、噪音监测、废水监测、报警记录等相关模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class MonitoringPoint(Base):
    """
    监测点位表
    存储环保监测点的基本信息
    """
    __tablename__ = "monitoring_points"
    
    id = Column(Integer, primary_key=True, index=True, comment="监测点ID")
    point_code = Column(String(50), unique=True, index=True, comment="监测点编号")
    point_name = Column(String(100), nullable=False, comment="监测点名称")
    location = Column(String(200), comment="监测点位置")
    monitoring_type = Column(String(20), nullable=False, comment="监测类型（粉尘、噪音、废水）")
    equipment_model = Column(String(100), comment="监测设备型号")
    installation_date = Column(Date, comment="安装日期")
    status = Column(String(20), default="正常", comment="设备状态（正常、故障、维护中）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    dust_records = relationship("DustMonitoring", back_populates="monitoring_point")
    noise_records = relationship("NoiseMonitoring", back_populates="monitoring_point")
    wastewater_records = relationship("WastewaterMonitoring", back_populates="monitoring_point")


class DustMonitoring(Base):
    """
    粉尘监测数据表
    记录粉尘浓度监测数据
    """
    __tablename__ = "dust_monitoring"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    monitoring_point_id = Column(Integer, ForeignKey("monitoring_points.id"), nullable=False, comment="监测点ID")
    record_time = Column(DateTime, index=True, default=datetime.now, comment="记录时间")
    record_date = Column(Date, index=True, comment="记录日期")
    pm25_concentration = Column(Float, default=0.0, comment="PM2.5浓度（μg/m³）")
    pm10_concentration = Column(Float, default=0.0, comment="PM10浓度（μg/m³）")
    tsp_concentration = Column(Float, default=0.0, comment="总悬浮颗粒物浓度（mg/m³）")
    is_over_limit = Column(Boolean, default=False, comment="是否超标")
    threshold_value = Column(Float, default=0.15, comment="浓度阈值（mg/m³）")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    monitoring_point = relationship("MonitoringPoint", back_populates="dust_records")
    alarms = relationship("AlarmRecord", back_populates="dust_monitoring")


class NoiseMonitoring(Base):
    """
    噪音监测数据表
    记录噪音分贝监测数据
    """
    __tablename__ = "noise_monitoring"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    monitoring_point_id = Column(Integer, ForeignKey("monitoring_points.id"), nullable=False, comment="监测点ID")
    record_time = Column(DateTime, index=True, default=datetime.now, comment="记录时间")
    record_date = Column(Date, index=True, comment="记录日期")
    db_value = Column(Float, default=0.0, comment="噪音值（dB）")
    frequency = Column(String(20), comment="频率范围")
    is_over_limit = Column(Boolean, default=False, comment="是否超标")
    threshold_value = Column(Float, default=85.0, comment="噪音阈值（dB）")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    monitoring_point = relationship("MonitoringPoint", back_populates="noise_records")
    alarms = relationship("AlarmRecord", back_populates="noise_monitoring")


class WastewaterMonitoring(Base):
    """
    废水监测数据表
    记录废水排放监测数据
    """
    __tablename__ = "wastewater_monitoring"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    monitoring_point_id = Column(Integer, ForeignKey("monitoring_points.id"), nullable=False, comment="监测点ID")
    record_time = Column(DateTime, index=True, default=datetime.now, comment="记录时间")
    record_date = Column(Date, index=True, comment="记录日期")
    ph_value = Column(Float, default=7.0, comment="PH值")
    cod_value = Column(Float, default=0.0, comment="COD值（mg/L）")
    ss_value = Column(Float, default=0.0, comment="悬浮物浓度（mg/L）")
    ammonia_nitrogen = Column(Float, default=0.0, comment="氨氮浓度（mg/L）")
    flow_rate = Column(Float, default=0.0, comment="流量（立方米/小时）")
    is_over_limit = Column(Boolean, default=False, comment="是否超标")
    ph_threshold_min = Column(Float, default=6.0, comment="PH值下限")
    ph_threshold_max = Column(Float, default=9.0, comment="PH值上限")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    monitoring_point = relationship("MonitoringPoint", back_populates="wastewater_records")
    alarms = relationship("AlarmRecord", back_populates="wastewater_monitoring")


class AlarmRecord(Base):
    """
    报警记录表
    记录环保监测数据超标的报警信息
    """
    __tablename__ = "alarm_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="报警记录ID")
    alarm_time = Column(DateTime, index=True, default=datetime.now, comment="报警时间")
    alarm_type = Column(String(20), nullable=False, comment="报警类型（粉尘超标、噪音超标、废水超标）")
    monitoring_point_id = Column(Integer, ForeignKey("monitoring_points.id"), nullable=True, comment="监测点ID")
    
    # 关联具体监测数据（三种类型，只会有一种有值）
    dust_monitoring_id = Column(Integer, ForeignKey("dust_monitoring.id"), nullable=True, comment="关联粉尘监测记录ID")
    noise_monitoring_id = Column(Integer, ForeignKey("noise_monitoring.id"), nullable=True, comment="关联噪音监测记录ID")
    wastewater_monitoring_id = Column(Integer, ForeignKey("wastewater_monitoring.id"), nullable=True, comment="关联废水监测记录ID")
    
    alarm_level = Column(String(20), default="一般", comment="报警级别（一般、重要、紧急）")
    actual_value = Column(Float, default=0.0, comment="实际值")
    threshold_value = Column(Float, default=0.0, comment="阈值")
    message = Column(String(500), comment="报警描述")
    is_handled = Column(Boolean, default=False, comment="是否已处理")
    handled_by = Column(String(50), comment="处理人")
    handled_time = Column(DateTime, nullable=True, comment="处理时间")
    handling_method = Column(String(500), comment="处理方式")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    dust_monitoring = relationship("DustMonitoring", back_populates="alarms")
    noise_monitoring = relationship("NoiseMonitoring", back_populates="alarms")
    wastewater_monitoring = relationship("WastewaterMonitoring", back_populates="alarms")
