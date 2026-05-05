"""
生产数据分析模块的数据库模型
包含产量统计、设备管理、能耗指标等相关模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Equipment(Base):
    """
    设备信息表
    存储生产设备的基本信息
    """
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True, comment="设备ID")
    equipment_code = Column(String(50), unique=True, index=True, comment="设备编号")
    equipment_name = Column(String(100), nullable=False, comment="设备名称")
    equipment_type = Column(String(50), comment="设备类型（搅拌机、运输车、泵车等")
    specification = Column(String(100), comment="设备规格型号")
    max_capacity = Column(Float, comment="最大产能（立方米/小时）")
    manufacturer = Column(String(100), comment="生产厂家")
    purchase_date = Column(Date, comment="购买日期")
    status = Column(String(20), default="正常", comment="设备状态（正常、维修中、停用）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    utilization_records = relationship("EquipmentUtilization", back_populates="equipment")
    energy_consumptions = relationship("EnergyConsumption", back_populates="equipment")


class ProductionRecord(Base):
    """
    生产记录表
    记录每日/每月的产量数据
    """
    __tablename__ = "production_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    record_date = Column(Date, unique=True, index=True, comment="记录日期")
    total_production = Column(Float, default=0.0, comment="当日总产量（立方米）")
    qualified_production = Column(Float, default=0.0, comment="合格产量（立方米）")
    batch_count = Column(Integer, default=0, comment="生产批次数量")
    working_hours = Column(Float, default=0.0, comment="当日工作时长（小时）")
    production_type = Column(String(50), comment="生产类型（商砼、预制件等")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class EquipmentUtilization(Base):
    """
    设备利用率记录表
    记录每台设备的运行时间和利用率
    """
    __tablename__ = "equipment_utilization"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    record_date = Column(Date, index=True, comment="记录日期")
    total_available_hours = Column(Float, default=24.0, comment="当日可用时长（小时）")
    actual_working_hours = Column(Float, default=0.0, comment="实际工作时长（小时）")
    maintenance_hours = Column(Float, default=0.0, comment="维护时长（小时）")
    idle_hours = Column(Float, default=0.0, comment="闲置时长（小时）")
    utilization_rate = Column(Float, default=0.0, comment="设备利用率（%）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    equipment = relationship("Equipment", back_populates="utilization_records")


class EnergyConsumption(Base):
    """
    能耗指标记录表
    记录能源消耗数据（电、水、燃料等）
    """
    __tablename__ = "energy_consumption"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    record_date = Column(Date, index=True, comment="记录日期")
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True, comment="关联设备ID（可为空，用于统计总能耗）")
    energy_type = Column(String(20), nullable=False, comment="能源类型（电力、水、柴油、天然气等）")
    consumption_amount = Column(Float, default=0.0, comment="消耗量（单位根据能源类型不同）")
    unit = Column(String(20), comment="单位（kWh、立方米、升等）")
    cost = Column(Float, default=0.0, comment="消耗成本（元）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    equipment = relationship("Equipment", back_populates="energy_consumptions")
