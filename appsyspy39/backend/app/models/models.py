"""
数据库模型模块 - 定义所有数据模型
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """基础模型类"""
    pass


class User(Base):
    """
    用户表 - 存储生产操作员信息
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), comment="联系电话")
    role = Column(String(20), default="operator", comment="角色：operator-操作员, admin-管理员")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    tasks_accepted = relationship("Task", back_populates="operator", foreign_keys="Task.operator_id")
    feeding_records = relationship("FeedingRecord", back_populates="operator")
    mixing_records = relationship("MixingRecord", back_populates="operator")


class Task(Base):
    """
    生产任务表 - 存储生产任务信息
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_no = Column(String(50), unique=True, index=True, nullable=False, comment="任务编号")
    concrete_grade = Column(String(20), nullable=False, comment="混凝土标号（如C30、C40）")
    quantity = Column(Float, nullable=False, comment="生产数量（立方米）")
    delivery_time = Column(DateTime, nullable=False, comment="交货时间")
    project_name = Column(String(100), nullable=False, comment="项目名称")
    project_address = Column(String(200), comment="项目地址")
    customer_name = Column(String(50), comment="客户名称")
    
    # 状态相关
    status = Column(String(20), default="pending", comment="状态：pending-待接, accepted-已接, in_progress-进行中, completed-已完成, cancelled-已取消")
    operator_id = Column(Integer, ForeignKey("users.id"), comment="接单人ID")
    accepted_at = Column(DateTime, comment="接单时间")
    started_at = Column(DateTime, comment="开始生产时间")
    completed_at = Column(DateTime, comment="完成时间")
    
    # 关联配方
    formula_id = Column(Integer, ForeignKey("formulas.id"), comment="使用的配方ID")
    
    # 备注
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    operator = relationship("User", back_populates="tasks_accepted", foreign_keys=[operator_id])
    formula = relationship("Formula", back_populates="tasks")
    feeding_records = relationship("FeedingRecord", back_populates="task")
    mixing_records = relationship("MixingRecord", back_populates="task")
    formula_adjustments = relationship("FormulaAdjustment", back_populates="task")


class Formula(Base):
    """
    配合比配方表 - 存储标准配合比信息
    """
    __tablename__ = "formulas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    formula_name = Column(String(100), nullable=False, comment="配方名称")
    formula_code = Column(String(50), unique=True, index=True, nullable=False, comment="配方编号")
    concrete_grade = Column(String(20), nullable=False, comment="适用混凝土标号")
    
    # 基础参数
    water_cement_ratio = Column(Float, nullable=False, comment="水灰比")
    slump = Column(Float, comment="坍落度（mm）")
    
    # 材料用量（每立方米用量，单位：kg）
    cement = Column(Float, nullable=False, comment="水泥用量")
    water = Column(Float, nullable=False, comment="用水量")
    sand = Column(Float, nullable=False, comment="砂子用量")
    stone = Column(Float, nullable=False, comment="石子用量")
    admixture = Column(Float, comment="外加剂用量")
    admixture_type = Column(String(50), comment="外加剂类型")
    
    # 其他材料
    fly_ash = Column(Float, default=0, comment="粉煤灰用量")
    mineral_powder = Column(Float, default=0, comment="矿粉用量")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_standard = Column(Boolean, default=True, comment="是否标准配方")
    
    remarks = Column(Text, comment="备注说明")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联关系
    tasks = relationship("Task", back_populates="formula")
    adjustments = relationship("FormulaAdjustment", back_populates="base_formula")


class FormulaAdjustment(Base):
    """
    配方调整记录表 - 记录配方微调历史
    """
    __tablename__ = "formula_adjustments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联信息
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="任务ID")
    base_formula_id = Column(Integer, ForeignKey("formulas.id"), nullable=False, comment="基础配方ID")
    operator_id = Column(Integer, ForeignKey("users.id"), comment="调整人ID")
    
    # 调整前参数（理论值）
    orig_water_cement_ratio = Column(Float, comment="原水灰比")
    orig_cement = Column(Float, comment="原水泥用量")
    orig_water = Column(Float, comment="原用水量")
    orig_sand = Column(Float, comment="原砂子用量")
    orig_stone = Column(Float, comment="原石子用量")
    orig_admixture = Column(Float, comment="原外加剂用量")
    orig_admixture_dosage = Column(Float, comment="原外加剂掺量百分比")
    
    # 调整后参数
    new_water_cement_ratio = Column(Float, comment="新水灰比")
    new_cement = Column(Float, comment="新水泥用量")
    new_water = Column(Float, comment="新用水量")
    new_sand = Column(Float, comment="新砂子用量")
    new_stone = Column(Float, comment="新石子用量")
    new_admixture = Column(Float, comment="新外加剂用量")
    new_admixture_dosage = Column(Float, comment="新外加剂掺量百分比")
    
    # 调整原因
    adjustment_reason = Column(Text, nullable=False, comment="调整原因")
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime, default=datetime.now, comment="调整时间")
    
    # 关联关系
    task = relationship("Task", back_populates="formula_adjustments")
    base_formula = relationship("Formula", back_populates="adjustments")


class FeedingRecord(Base):
    """
    投料记录表 - 记录每盘原材料投料情况
    """
    __tablename__ = "feeding_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联信息
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="任务ID")
    operator_id = Column(Integer, ForeignKey("users.id"), comment="投料操作员ID")
    
    # 盘信息
    batch_no = Column(Integer, nullable=False, comment="盘号（第几盘）")
    batch_quantity = Column(Float, nullable=False, comment="本盘方量")
    
    # 投料方式
    feeding_method = Column(String(20), default="manual", comment="投料方式：scan-扫码录入, manual-手动录入")
    
    # 原材料扫码/录入信息
    cement_barcode = Column(String(100), comment="水泥条码")
    cement_lot = Column(String(50), comment="水泥批号")
    cement_actual = Column(Float, comment="水泥实际用量(kg)")
    
    water_actual = Column(Float, comment="水实际用量(kg)")
    
    sand_barcode = Column(String(100), comment="砂子条码")
    sand_lot = Column(String(50), comment="砂子批号")
    sand_actual = Column(Float, comment="砂子实际用量(kg)")
    
    stone_barcode = Column(String(100), comment="石子条码")
    stone_lot = Column(String(50), comment="石子批号")
    stone_actual = Column(Float, comment="石子实际用量(kg)")
    
    admixture_barcode = Column(String(100), comment="外加剂条码")
    admixture_lot = Column(String(50), comment="外加剂批号")
    admixture_actual = Column(Float, comment="外加剂实际用量(kg)")
    
    fly_ash_actual = Column(Float, default=0, comment="粉煤灰实际用量(kg)")
    mineral_powder_actual = Column(Float, default=0, comment="矿粉实际用量(kg)")
    
    # 偏差计算结果
    cement_deviation = Column(Float, comment="水泥偏差百分比")
    water_deviation = Column(Float, comment="水偏差百分比")
    sand_deviation = Column(Float, comment="砂子偏差百分比")
    stone_deviation = Column(Float, comment="石子偏差百分比")
    admixture_deviation = Column(Float, comment="外加剂偏差百分比")
    
    # 预警状态
    has_warning = Column(Boolean, default=False, comment="是否有预警")
    warning_level = Column(String(20), comment="预警级别：warning-警告, critical-严重")
    warning_message = Column(Text, comment="预警信息")
    
    # 理论用量（根据配方和盘方量计算）
    cement_theory = Column(Float, comment="水泥理论用量")
    water_theory = Column(Float, comment="水理论用量")
    sand_theory = Column(Float, comment="砂子理论用量")
    stone_theory = Column(Float, comment="石子理论用量")
    admixture_theory = Column(Float, comment="外加剂理论用量")
    
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime, default=datetime.now, comment="投料时间")
    
    # 关联关系
    task = relationship("Task", back_populates="feeding_records")
    operator = relationship("User", back_populates="feeding_records")


class MixingRecord(Base):
    """
    搅拌过程记录表 - 记录每盘搅拌过程数据
    """
    __tablename__ = "mixing_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联信息
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="任务ID")
    feeding_record_id = Column(Integer, ForeignKey("feeding_records.id"), comment="关联投料记录ID")
    operator_id = Column(Integer, ForeignKey("users.id"), comment="操作员ID")
    
    # 盘信息
    batch_no = Column(Integer, nullable=False, comment="盘号")
    
    # 搅拌参数
    mixing_time_seconds = Column(Integer, nullable=False, comment="搅拌时长（秒）")
    rotation_speed = Column(Integer, comment="搅拌转速（RPM）")
    current_temperature = Column(Float, comment="当前温度（℃）")
    
    # 搅拌状态
    status = Column(String(20), default="completed", comment="状态：mixing-搅拌中, completed-已完成, abnormal-异常")
    
    # 异常记录
    is_abnormal = Column(Boolean, default=False, comment="是否异常")
    abnormal_type = Column(String(50), comment="异常类型：material_shortage-缺料, equipment_fault-设备故障, quality_issue-质量问题, other-其他")
    abnormal_description = Column(Text, comment="异常情况说明")
    handling_measures = Column(Text, comment="处理措施")
    
    # 质量检验
    slump_actual = Column(Float, comment="实测坍落度（mm）")
    temperature_actual = Column(Float, comment="实测温度（℃）")
    quality_status = Column(String(20), comment="质量状态：qualified-合格, unqualified-不合格")
    
    remarks = Column(Text, comment="备注")
    
    created_at = Column(DateTime, default=datetime.now, comment="记录时间")
    completed_at = Column(DateTime, comment="搅拌完成时间")
    
    # 关联关系
    task = relationship("Task", back_populates="mixing_records")
    operator = relationship("User", back_populates="mixing_records")
