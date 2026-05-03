from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Device(Base):
    """
    物联网设备表
    存储环境监测设备的基本信息
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True, comment="设备ID")
    device_code = Column(String(50), unique=True, index=True, nullable=False, comment="设备编号")
    device_name = Column(String(100), nullable=False, comment="设备名称")
    device_type = Column(String(50), nullable=False, comment="设备类型（如：温湿度传感器、光照传感器等）")
    location = Column(String(200), comment="安装位置")
    status = Column(String(20), default="online", comment="设备状态（online/offline/maintenance）")
    description = Column(Text, comment="设备描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联环境数据
    environment_data = relationship("EnvironmentData", back_populates="device")


class EnvironmentData(Base):
    """
    环境数据表
    存储物联网设备采集的环境数据
    """
    __tablename__ = "environment_data"

    id = Column(Integer, primary_key=True, index=True, comment="数据ID")
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, comment="关联设备ID")
    temperature = Column(Float, comment="空气温度（℃）")
    humidity = Column(Float, comment="空气湿度（%）")
    light_intensity = Column(Float, comment="光照强度（Lux）")
    soil_moisture = Column(Float, comment="土壤水分（%）")
    co2_concentration = Column(Float, comment="CO₂浓度（ppm）")
    recorded_at = Column(DateTime, default=datetime.now, index=True, comment="记录时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关联设备
    device = relationship("Device", back_populates="environment_data")


class Crop(Base):
    """
    作物表
    存储作物基本信息
    """
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True, comment="作物ID")
    crop_name = Column(String(100), nullable=False, comment="作物名称")
    crop_type = Column(String(50), comment="作物类型")
    variety = Column(String(100), comment="品种")
    planting_date = Column(DateTime, comment="种植日期")
    expected_harvest_date = Column(DateTime, comment="预计收获日期")
    location = Column(String(200), comment="种植位置")
    status = Column(String(20), default="growing", comment="作物状态（growing/harvested/diseased）")
    notes = Column(Text, comment="备注信息")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联生长记录
    growth_records = relationship("GrowthRecord", back_populates="crop")


class GrowthRecord(Base):
    """
    生长状态记录表
    存储作物生长过程中的照片、视频和状态记录
    """
    __tablename__ = "growth_records"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, comment="关联作物ID")
    record_type = Column(String(20), nullable=False, comment="记录类型（image/video/text）")
    title = Column(String(200), comment="记录标题")
    description = Column(Text, comment="详细描述")
    file_path = Column(String(500), comment="文件路径（图片或视频）")
    file_type = Column(String(50), comment="文件类型")
    
    # 生育期信息
    growth_stage = Column(String(50), comment="生育期（出苗期/开花期/结果期/成熟期等）")
    
    # AI识别结果
    ai_diagnosis = Column(Text, comment="AI图像识别诊断结果")
    disease_detected = Column(String(100), comment="检测到的病害")
    nutrition_status = Column(String(100), comment="营养状况评估")
    diagnosis_confidence = Column(Float, comment="诊断置信度")
    
    recorded_at = Column(DateTime, default=datetime.now, index=True, comment="记录时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关联作物
    crop = relationship("Crop", back_populates="growth_records")
