"""
数据库模型定义
包含系统所需的所有数据库表结构
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    用户表
    存储系统用户信息，支持不同角色
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    role = Column(String(20), default="inspector")  # inspector: 检验员, admin: 管理员
    phone = Column(String(20))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Material(Base):
    """
    原材料表
    存储原材料基本信息
    """
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    material_code = Column(String(50), unique=True, index=True, nullable=False)
    material_name = Column(String(100), nullable=False)
    material_type = Column(String(50), nullable=False)  # cement: 水泥, aggregate: 骨料, admixture: 外加剂
    supplier = Column(String(100))
    specification = Column(String(100))
    unit = Column(String(20), default="吨")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MaterialInspection(Base):
    """
    原材料检验记录表
    存储原材料进场检验数据
    """
    __tablename__ = "material_inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    inspection_no = Column(String(50), unique=True, index=True, nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    batch_no = Column(String(100), nullable=False)
    arrival_date = Column(DateTime, nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 检验指标
    cement_strength_3d = Column(Float)  # 水泥3天强度
    cement_strength_28d = Column(Float)  # 水泥28天强度
    cement_fineness = Column(Float)  # 水泥细度
    aggregate_gradation = Column(Text)  # 骨料级配数据（JSON格式）
    admixture_performance = Column(Text)  # 外加剂性能数据（JSON格式）
    water_content = Column(Float)  # 含水量
    impurity_content = Column(Float)  # 杂质含量
    
    # 检验结果
    inspection_date = Column(DateTime, default=datetime.utcnow)
    is_qualified = Column(Boolean, default=True)
    status = Column(String(20), default="合格")  # 合格: qualified, 不合格: disabled
    inspection_report = Column(String(255))  # 检验报告附件路径
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    material = relationship("Material")
    inspector = relationship("User")


class ProductionFormula(Base):
    """
    生产配方表
    存储混凝土生产配方
    """
    __tablename__ = "production_formulas"
    
    id = Column(Integer, primary_key=True, index=True)
    formula_code = Column(String(50), unique=True, index=True, nullable=False)
    formula_name = Column(String(100), nullable=False)
    concrete_grade = Column(String(20), nullable=False)  # 混凝土强度等级
    description = Column(Text)
    
    # 配方比例（单位：kg/m³）
    cement_amount = Column(Float, nullable=False)  # 水泥用量
    sand_amount = Column(Float, nullable=False)  # 砂用量
    stone_amount = Column(Float, nullable=False)  # 石用量
    water_amount = Column(Float, nullable=False)  # 水用量
    admixture_amount = Column(Float)  # 外加剂用量
    fly_ash_amount = Column(Float)  # 粉煤灰用量
    
    # 允许偏差范围
    cement_tolerance = Column(Float, default=2.0)  # 水泥允许偏差±%
    aggregate_tolerance = Column(Float, default=3.0)  # 骨料允许偏差±%
    water_tolerance = Column(Float, default=1.0)  # 水允许偏差±%
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductionRecord(Base):
    """
    生产记录表
    存储混凝土生产记录
    """
    __tablename__ = "production_records"
    
    id = Column(Integer, primary_key=True, index=True)
    production_no = Column(String(50), unique=True, index=True, nullable=False)
    formula_id = Column(Integer, ForeignKey("production_formulas.id"), nullable=False)
    qr_code = Column(String(100), unique=True, index=True, nullable=False)  # 二维码标识
    truck_no = Column(String(20), nullable=False)  # 罐车编号
    
    # 生产参数
    mix_volume = Column(Float, nullable=False)  # 搅拌方量
    mix_duration = Column(Integer, nullable=False)  # 搅拌时间（秒）
    target_mix_duration = Column(Integer, nullable=False)  # 目标搅拌时间（秒）
    
    # 投料记录（JSON格式，存储实际投料数据）
    feeding_data = Column(Text)
    
    # 生产状态
    production_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="正常")  # 正常: normal, 异常: abnormal
    operator_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    formula = relationship("ProductionFormula")
    operator = relationship("User")


class QualityAlert(Base):
    """
    质量异常预警表
    存储质量异常预警信息
    """
    __tablename__ = "quality_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_no = Column(String(50), unique=True, index=True, nullable=False)
    production_id = Column(Integer, ForeignKey("production_records.id"), nullable=False)
    
    alert_type = Column(String(50), nullable=False)  # mix_ratio_deviation: 配比偏差, mix_time_short: 搅拌时间不足, material_unqualified: 原材料不合格
    alert_level = Column(String(20), default="一般")  # 一般: normal, 严重: serious, 紧急: urgent
    
    description = Column(Text, nullable=False)
    deviation_data = Column(Text)  # 偏差数据（JSON格式）
    
    # 处理状态
    status = Column(String(20), default="待处理")  # 待处理: pending, 处理中: processing, 已处理: resolved
    handler_id = Column(Integer, ForeignKey("users.id"))
    handle_time = Column(DateTime)
    handle_result = Column(Text)
    
    # 通知信息
    notified_inspectors = Column(Text)  # 已通知检验员（JSON格式）
    notified_admins = Column(Text)  # 已通知管理员（JSON格式）
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    production = relationship("ProductionRecord")
    handler = relationship("User")


class InspectionReport(Base):
    """
    检验报告表
    存储各类检验报告
    """
    __tablename__ = "inspection_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_no = Column(String(50), unique=True, index=True, nullable=False)
    production_id = Column(Integer, ForeignKey("production_records.id"), nullable=False)
    
    report_type = Column(String(50), nullable=False)  # 出厂检验: factory, 现场检验: site
    inspection_date = Column(DateTime, nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 检验指标
    slump = Column(Float)  # 坍落度
    air_content = Column(Float)  # 含气量
    temperature = Column(Float)  # 温度
    strength_7d = Column(Float)  # 7天强度
    strength_28d = Column(Float)  # 28天强度
    
    report_file = Column(String(255))  # 报告文件路径
    is_qualified = Column(Boolean, default=True)
    remarks = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    production = relationship("ProductionRecord")
    inspector = relationship("User")


class FeedingRecord(Base):
    """
    投料记录表
    存储详细的投料记录
    """
    __tablename__ = "feeding_records"
    
    id = Column(Integer, primary_key=True, index=True)
    production_id = Column(Integer, ForeignKey("production_records.id"), nullable=False)
    material_type = Column(String(50), nullable=False)  # 材料类型
    
    target_amount = Column(Float, nullable=False)  # 目标用量
    actual_amount = Column(Float, nullable=False)  # 实际用量
    deviation = Column(Float)  # 偏差量
    deviation_percent = Column(Float)  # 偏差百分比
    
    feeding_time = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    production = relationship("ProductionRecord")
