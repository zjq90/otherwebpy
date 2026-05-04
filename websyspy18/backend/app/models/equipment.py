"""
工程维保管理模块 - 数据模型
包含设备台账、巡检计划、保养计划、故障维修记录等模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Equipment(Base):
    """
    设备台账模型
    存储电梯、水泵等设备的基本信息
    """
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="设备名称")
    code = Column(String(50), unique=True, index=True, comment="设备编号")
    category = Column(String(50), nullable=False, comment="设备类别（电梯、水泵、空调等）")
    model = Column(String(100), comment="设备型号")
    manufacturer = Column(String(100), comment="生产厂家")
    purchase_date = Column(Date, comment="购买日期")
    warranty_expiry = Column(Date, comment="保修到期日期")
    location = Column(String(200), comment="安装位置")
    status = Column(String(20), default="正常", comment="设备状态（正常、故障、维修中、报废）")
    description = Column(Text, comment="设备描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    inspection_plans = relationship("InspectionPlan", back_populates="equipment")
    maintenance_plans = relationship("MaintenancePlan", back_populates="equipment")
    faults = relationship("FaultRecord", back_populates="equipment")

class InspectionPlan(Base):
    """
    巡检计划表
    记录设备的巡检计划安排
    """
    __tablename__ = "inspection_plans"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    plan_name = Column(String(100), nullable=False, comment="计划名称")
    cycle = Column(String(50), comment="巡检周期（每日、每周、每月、季度、年度）")
    next_inspection_date = Column(Date, comment="下次巡检日期")
    inspector = Column(String(50), comment="巡检负责人")
    items = Column(Text, comment="巡检项目（JSON格式）")
    status = Column(String(20), default="待执行", comment="计划状态（待执行、执行中、已完成、已取消）")
    description = Column(Text, comment="备注说明")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    equipment = relationship("Equipment", back_populates="inspection_plans")
    records = relationship("InspectionRecord", back_populates="plan")

class InspectionRecord(Base):
    """
    巡检记录表
    记录每次巡检的实际结果
    """
    __tablename__ = "inspection_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("inspection_plans.id"), nullable=False, comment="巡检计划ID")
    inspection_date = Column(Date, nullable=False, comment="巡检日期")
    inspector = Column(String(50), comment="巡检人")
    result = Column(String(20), default="正常", comment="巡检结果（正常、异常）")
    issues = Column(Text, comment="发现的问题")
    suggestion = Column(Text, comment="处理建议")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    plan = relationship("InspectionPlan", back_populates="records")

class MaintenancePlan(Base):
    """
    保养计划表
    记录设备的保养计划安排
    """
    __tablename__ = "maintenance_plans"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    plan_name = Column(String(100), nullable=False, comment="计划名称")
    cycle = Column(String(50), comment="保养周期（每月、季度、半年、年度）")
    next_maintenance_date = Column(Date, comment="下次保养日期")
    maintainer = Column(String(50), comment="保养负责人")
    items = Column(Text, comment="保养项目（JSON格式）")
    estimated_cost = Column(Float, default=0, comment="预估费用")
    status = Column(String(20), default="待执行", comment="计划状态（待执行、执行中、已完成、已取消）")
    description = Column(Text, comment="备注说明")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    equipment = relationship("Equipment", back_populates="maintenance_plans")
    records = relationship("MaintenanceRecord", back_populates="plan")

class MaintenanceRecord(Base):
    """
    保养记录表
    记录每次保养的实际情况
    """
    __tablename__ = "maintenance_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("maintenance_plans.id"), nullable=False, comment="保养计划ID")
    maintenance_date = Column(Date, nullable=False, comment="保养日期")
    maintainer = Column(String(50), comment="保养人")
    items_done = Column(Text, comment="完成的保养项目（JSON格式）")
    actual_cost = Column(Float, default=0, comment="实际费用")
    result = Column(String(20), default="完成", comment="保养结果")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关系定义
    plan = relationship("MaintenancePlan", back_populates="records")

class FaultRecord(Base):
    """
    故障维修记录表
    记录设备故障及维修全过程
    """
    __tablename__ = "fault_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    fault_code = Column(String(50), unique=True, index=True, comment="故障编号")
    fault_type = Column(String(50), comment="故障类型")
    fault_description = Column(Text, nullable=False, comment="故障描述")
    report_time = Column(DateTime, default=datetime.now, comment="故障报修时间")
    reporter = Column(String(50), comment="报修人")
    assign_to = Column(String(50), comment="维修负责人")
    start_time = Column(DateTime, comment="维修开始时间")
    end_time = Column(DateTime, comment="维修完成时间")
    solution = Column(Text, comment="维修方案")
    parts_used = Column(Text, comment="使用配件（JSON格式）")
    labor_cost = Column(Float, default=0, comment="人工费用")
    parts_cost = Column(Float, default=0, comment="配件费用")
    total_cost = Column(Float, default=0, comment="总费用")
    status = Column(String(20), default="待处理", comment="故障状态（待处理、处理中、已完成、已关闭）")
    satisfaction = Column(Integer, comment="满意度（1-5分）")
    description = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    equipment = relationship("Equipment", back_populates="faults")
