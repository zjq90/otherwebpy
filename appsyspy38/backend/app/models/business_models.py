"""
业务相关数据模型
包含拌合站、试验检测、物资采购、资源调度等业务模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Date
from sqlalchemy.orm import relationship
from ..database import Base


class ProductionTask(Base):
    """
    生产任务模型
    拌合站操作员的生产任务
    """
    __tablename__ = 'production_tasks'

    id = Column(Integer, primary_key=True, index=True, comment='任务ID')
    task_no = Column(String(50), unique=True, index=True, comment='任务编号')
    project_name = Column(String(200), comment='项目名称')
    concrete_type = Column(String(50), comment='混凝土类型')
    volume = Column(Float, comment='方量(立方米)')
    delivery_location = Column(String(500), comment='浇筑地点')
    required_time = Column(DateTime, comment='要求时间')
    operator_id = Column(Integer, ForeignKey('users.id'), comment='操作员ID')
    status = Column(String(20), default='pending', comment='状态: pending待执行, executing执行中, completed已完成')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    operator = relationship('User', foreign_keys=[operator_id])
    records = relationship('ProductionRecord', back_populates='task')


class ProductionRecord(Base):
    """
    生产记录模型
    拌合站操作员提交的生产记录
    """
    __tablename__ = 'production_records'

    id = Column(Integer, primary_key=True, index=True, comment='记录ID')
    task_id = Column(Integer, ForeignKey('production_tasks.id'), comment='任务ID')
    operator_id = Column(Integer, ForeignKey('users.id'), comment='操作员ID')
    production_date = Column(Date, comment='生产日期')
    concrete_type = Column(String(50), comment='混凝土类型')
    actual_volume = Column(Float, comment='实际方量')
    slump = Column(String(50), comment='坍落度')
    temperature = Column(Float, comment='出机温度')
    equipment_no = Column(String(50), comment='设备编号')
    batch_no = Column(String(50), comment='批次号')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系
    task = relationship('ProductionTask', back_populates='records')
    operator = relationship('User', foreign_keys=[operator_id])


class MaterialInspection(Base):
    """
    原材料检验模型
    试验检测员录入的原材料检验数据
    """
    __tablename__ = 'material_inspections'

    id = Column(Integer, primary_key=True, index=True, comment='检验ID')
    inspection_no = Column(String(50), unique=True, index=True, comment='检验编号')
    material_type = Column(String(50), comment='材料类型: 水泥、砂石、外加剂等')
    material_name = Column(String(100), comment='材料名称')
    batch_no = Column(String(50), comment='批次号')
    supplier = Column(String(100), comment='供应商')
    quantity = Column(Float, comment='数量')
    inspector_id = Column(Integer, ForeignKey('users.id'), comment='检验员ID')
    inspection_date = Column(Date, comment='检验日期')
    inspection_result = Column(String(20), comment='检验结果: qualified合格, unqualified不合格')
    inspection_items = Column(Text, comment='检验项目明细(JSON格式)')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    inspector = relationship('User', foreign_keys=[inspector_id])


class QualityReport(Base):
    """
    成品质量报告模型
    试验检测员查看的成品质量报告
    """
    __tablename__ = 'quality_reports'

    id = Column(Integer, primary_key=True, index=True, comment='报告ID')
    report_no = Column(String(50), unique=True, index=True, comment='报告编号')
    project_name = Column(String(200), comment='项目名称')
    concrete_type = Column(String(50), comment='混凝土类型')
    batch_no = Column(String(50), comment='批次号')
    production_date = Column(Date, comment='生产日期')
    strength_grade = Column(String(50), comment='强度等级')
    test_age = Column(Integer, comment='试验龄期(天)')
    compressive_strength = Column(Float, comment='抗压强度(MPa)')
    flexural_strength = Column(Float, nullable=True, comment='抗折强度(MPa)')
    inspector_id = Column(Integer, ForeignKey('users.id'), comment='检验员ID')
    report_date = Column(Date, comment='报告日期')
    conclusion = Column(String(20), comment='结论: qualified合格, unqualified不合格')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    # 关系
    inspector = relationship('User', foreign_keys=[inspector_id])


class QualityAlert(Base):
    """
    质量预警模型
    试验检测员发起的质量异常预警
    """
    __tablename__ = 'quality_alerts'

    id = Column(Integer, primary_key=True, index=True, comment='预警ID')
    alert_no = Column(String(50), unique=True, index=True, comment='预警编号')
    alert_type = Column(String(50), comment='预警类型')
    alert_level = Column(String(20), comment='预警级别: low一般, medium严重, high紧急')
    project_name = Column(String(200), comment='项目名称')
    concrete_type = Column(String(50), comment='混凝土类型')
    batch_no = Column(String(50), comment='批次号')
    description = Column(Text, comment='问题描述')
    initiator_id = Column(Integer, ForeignKey('users.id'), comment='发起人ID')
    status = Column(String(20), default='pending', comment='状态: pending待处理, processing处理中, resolved已解决')
    handler_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment='处理人ID')
    handle_result = Column(Text, nullable=True, comment='处理结果')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    initiator = relationship('User', foreign_keys=[initiator_id])
    handler = relationship('User', foreign_keys=[handler_id])


class MaterialInventory(Base):
    """
    原材料库存模型
    物资采购员查看的原材料库存
    """
    __tablename__ = 'material_inventories'

    id = Column(Integer, primary_key=True, index=True, comment='库存ID')
    material_code = Column(String(50), unique=True, index=True, comment='材料编码')
    material_name = Column(String(100), comment='材料名称')
    material_type = Column(String(50), comment='材料类型')
    specification = Column(String(100), comment='规格型号')
    unit = Column(String(20), comment='单位')
    quantity = Column(Float, comment='库存数量')
    min_warning = Column(Float, comment='最低预警值')
    supplier = Column(String(100), comment='供应商')
    warehouse = Column(String(50), comment='仓库')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class PurchaseRequest(Base):
    """
    采购申请模型
    物资采购员提交的采购申请
    """
    __tablename__ = 'purchase_requests'

    id = Column(Integer, primary_key=True, index=True, comment='申请ID')
    request_no = Column(String(50), unique=True, index=True, comment='申请编号')
    applicant_id = Column(Integer, ForeignKey('users.id'), comment='申请人ID')
    material_name = Column(String(100), comment='材料名称')
    specification = Column(String(100), comment='规格型号')
    quantity = Column(Float, comment='申请数量')
    unit = Column(String(20), comment='单位')
    expected_price = Column(Float, nullable=True, comment='预估单价')
    supplier = Column(String(100), nullable=True, comment='推荐供应商')
    reason = Column(Text, comment='申请原因')
    urgency = Column(String(20), default='normal', comment='紧急程度: normal正常, urgent紧急')
    status = Column(String(20), default='pending', comment='状态: pending待审批, approved已批准, rejected已拒绝, completed已完成')
    approver_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment='审批人ID')
    approval_opinion = Column(Text, nullable=True, comment='审批意见')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    applicant = relationship('User', foreign_keys=[applicant_id])
    approver = relationship('User', foreign_keys=[approver_id])


class Supplier(Base):
    """
    供应商模型
    物资采购员跟踪的供应商信息
    """
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, index=True, comment='供应商ID')
    supplier_code = Column(String(50), unique=True, index=True, comment='供应商编码')
    supplier_name = Column(String(200), comment='供应商名称')
    contact_person = Column(String(50), comment='联系人')
    phone = Column(String(20), comment='联系电话')
    address = Column(String(500), comment='地址')
    business_scope = Column(String(500), comment='经营范围')
    credit_rating = Column(String(20), nullable=True, comment='信用等级')
    is_active = Column(Boolean, default=True, comment='是否合作中')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class Vehicle(Base):
    """
    车辆模型
    资源调度员查看的车辆信息
    """
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, index=True, comment='车辆ID')
    vehicle_no = Column(String(50), unique=True, index=True, comment='车牌号')
    vehicle_type = Column(String(50), comment='车辆类型: 搅拌车、泵车等')
    load_capacity = Column(Float, comment='载重能力(吨)')
    volume_capacity = Column(Float, nullable=True, comment='容积(立方米)')
    driver_name = Column(String(50), comment='驾驶员姓名')
    driver_phone = Column(String(20), comment='驾驶员电话')
    status = Column(String(20), default='idle', comment='状态: idle空闲, busy作业中, maintenance维护中')
    current_location = Column(String(200), nullable=True, comment='当前位置')
    latitude = Column(Float, nullable=True, comment='纬度')
    longitude = Column(Float, nullable=True, comment='经度')
    location_updated_at = Column(DateTime, nullable=True, comment='位置更新时间')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')


class TransportTask(Base):
    """
    运输任务模型
    资源调度员安排的运输任务
    """
    __tablename__ = 'transport_tasks'

    id = Column(Integer, primary_key=True, index=True, comment='任务ID')
    task_no = Column(String(50), unique=True, index=True, comment='任务编号')
    project_name = Column(String(200), comment='项目名称')
    delivery_location = Column(String(500), comment='送达地点')
    concrete_type = Column(String(50), comment='混凝土类型')
    volume = Column(Float, comment='方量(立方米)')
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), comment='车辆ID')
    scheduler_id = Column(Integer, ForeignKey('users.id'), comment='调度员ID')
    scheduled_time = Column(DateTime, comment='计划时间')
    actual_departure_time = Column(DateTime, nullable=True, comment='实际出发时间')
    actual_arrival_time = Column(DateTime, nullable=True, comment='实际到达时间')
    status = Column(String(20), default='pending', comment='状态: pending待执行, in_transit运输中, completed已完成')
    progress = Column(Integer, default=0, comment='进度百分比')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

    # 关系
    vehicle = relationship('Vehicle', foreign_keys=[vehicle_id])
    scheduler = relationship('User', foreign_keys=[scheduler_id])
