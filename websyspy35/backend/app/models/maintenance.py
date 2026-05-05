from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.core.database import Base


class MaintenancePlan(Base):
    """
    保养计划表
    制定周期性保养任务的计划模板
    """
    
    __tablename__ = "maintenance_plan"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 计划编号
    plan_code = Column(String(50), unique=True, index=True, nullable=False, comment="计划编号")
    
    # 计划名称
    name = Column(String(200), nullable=False, comment="计划名称")
    
    # 保养类型：日常保养、月度保养、季度保养、年度保养等
    maintenance_type = Column(String(50), nullable=False, comment="保养类型")
    
    # 执行周期（天数）
    cycle_days = Column(Integer, nullable=False, comment="执行周期（天数）")
    
    # 周期描述
    cycle_description = Column(String(100), comment="周期描述")
    
    # 保养内容
    content = Column(Text, nullable=False, comment="保养内容")
    
    # 保养标准
    standard = Column(Text, comment="保养标准")
    
    # 预计耗时（小时）
    estimated_hours = Column(Float, comment="预计耗时（小时）")
    
    # 负责人
    responsible_person = Column(String(50), comment="负责人")
    
    # 计划状态：启用、禁用
    status = Column(String(20), default="启用", comment="计划状态")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：关联保养任务
    maintenance_tasks = relationship("MaintenanceTask", back_populates="maintenance_plan", cascade="all, delete-orphan")


class MaintenanceTask(Base):
    """
    保养任务单表
    根据保养计划生成的具体保养任务单
    """
    
    __tablename__ = "maintenance_task"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 任务编号
    task_code = Column(String(50), unique=True, index=True, nullable=False, comment="任务编号")
    
    # 关联的保养计划ID
    plan_id = Column(Integer, ForeignKey("maintenance_plan.id"), index=True, comment="关联计划ID")
    
    # 关联的设备ID
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, index=True, comment="关联设备ID")
    
    # 任务名称
    name = Column(String(200), nullable=False, comment="任务名称")
    
    # 保养类型
    maintenance_type = Column(String(50), nullable=False, comment="保养类型")
    
    # 计划执行日期
    plan_date = Column(Date, nullable=False, comment="计划执行日期")
    
    # 实际执行日期
    actual_date = Column(Date, comment="实际执行日期")
    
    # 保养内容
    content = Column(Text, nullable=False, comment="保养内容")
    
    # 保养标准
    standard = Column(Text, comment="保养标准")
    
    # 负责人
    responsible_person = Column(String(50), comment="负责人")
    
    # 执行人员
    executor = Column(String(100), comment="执行人员")
    
    # 任务状态：待执行、执行中、已完成、已逾期、已取消
    status = Column(String(20), default="待执行", comment="任务状态")
    
    # 完成情况
    completion_status = Column(String(50), comment="完成情况")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：关联保养计划
    maintenance_plan = relationship("MaintenancePlan", back_populates="maintenance_tasks")
    
    # 关系：关联设备
    equipment = relationship("Equipment", back_populates="maintenance_tasks")
    
    # 关系：关联保养记录
    maintenance_records = relationship("MaintenanceRecord", back_populates="maintenance_task", cascade="all, delete-orphan")


class MaintenanceRecord(Base):
    """
    保养记录表
    记录保养任务的具体执行情况和结果
    """
    
    __tablename__ = "maintenance_record"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 记录编号
    record_code = Column(String(50), unique=True, index=True, nullable=False, comment="记录编号")
    
    # 关联的保养任务ID
    task_id = Column(Integer, ForeignKey("maintenance_task.id"), nullable=False, index=True, comment="关联任务ID")
    
    # 执行日期
    execution_date = Column(Date, nullable=False, comment="执行日期")
    
    # 执行人员
    executor = Column(String(100), nullable=False, comment="执行人员")
    
    # 工作时长（小时）
    work_hours = Column(Float, comment="工作时长（小时）")
    
    # 保养内容
    content = Column(Text, nullable=False, comment="保养内容")
    
    # 保养结果
    result = Column(Text, nullable=False, comment="保养结果")
    
    # 是否发现问题
    has_issues = Column(Boolean, default=False, comment="是否发现问题")
    
    # 问题描述
    issue_description = Column(Text, comment="问题描述")
    
    # 处理措施
    treatment_measures = Column(Text, comment="处理措施")
    
    # 更换的零部件
    replaced_parts = Column(Text, comment="更换的零部件")
    
    # 下次保养建议
    next_maintenance_suggestion = Column(Text, comment="下次保养建议")
    
    # 验收人员
    inspector = Column(String(50), comment="验收人员")
    
    # 验收日期
    inspection_date = Column(Date, comment="验收日期")
    
    # 验收结果：合格、不合格
    inspection_result = Column(String(20), comment="验收结果")
    
    # 备注信息
    description = Column(Text, comment="备注信息")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：关联保养任务
    maintenance_task = relationship("MaintenanceTask", back_populates="maintenance_records")
