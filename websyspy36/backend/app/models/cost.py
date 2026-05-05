"""
成本核算与利润分析模块的数据库模型
包含原材料成本、人工成本、能耗成本、销售数据等相关模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Material(Base):
    """
    原材料信息表
    存储生产所需的各种原材料信息
    """
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True, comment="原材料ID")
    material_code = Column(String(50), unique=True, index=True, comment="原材料编号")
    material_name = Column(String(100), nullable=False, comment="原材料名称")
    material_type = Column(String(50), comment="原材料类型（水泥、砂石、粉煤灰、外加剂等）")
    unit = Column(String(20), default="吨", comment="计量单位")
    current_price = Column(Float, default=0.0, comment="当前单价（元/单位）")
    supplier = Column(String(100), comment="供应商")
    stock_quantity = Column(Float, default=0.0, comment="库存量")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    cost_records = relationship("MaterialCost", back_populates="material")


class MaterialCost(Base):
    """
    原材料成本记录表
    记录每日原材料消耗和成本
    """
    __tablename__ = "material_costs"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    record_date = Column(Date, index=True, comment="记录日期")
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, comment="原材料ID")
    consumption_quantity = Column(Float, default=0.0, comment="消耗量")
    unit_price = Column(Float, default=0.0, comment="单价（元/单位）")
    total_cost = Column(Float, default=0.0, comment="总成本（元）")
    production_batch = Column(String(50), comment="关联生产批次")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    material = relationship("Material", back_populates="cost_records")


class Employee(Base):
    """
    员工信息表
    存储员工基本信息，用于人工成本核算
    """
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True, comment="员工ID")
    employee_code = Column(String(50), unique=True, index=True, comment="员工编号")
    employee_name = Column(String(50), nullable=False, comment="员工姓名")
    department = Column(String(50), comment="所属部门")
    position = Column(String(50), comment="职位")
    base_salary = Column(Float, default=0.0, comment="基本工资（元/月）")
    hourly_rate = Column(Float, default=0.0, comment="小时工资（元/小时）")
    status = Column(String(20), default="在职", comment="状态（在职、离职、休假）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    labor_costs = relationship("LaborCost", back_populates="employee")


class LaborCost(Base):
    """
    人工成本记录表
    记录每日人工工时和成本
    """
    __tablename__ = "labor_costs"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    record_date = Column(Date, index=True, comment="记录日期")
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="员工ID")
    working_hours = Column(Float, default=0.0, comment="工作时长（小时）")
    overtime_hours = Column(Float, default=0.0, comment="加班时长（小时）")
    hourly_rate = Column(Float, default=0.0, comment="小时工资（元/小时）")
    overtime_rate = Column(Float, default=0.0, comment="加班工资倍率")
    total_labor_cost = Column(Float, default=0.0, comment="当日人工总成本（元）")
    work_content = Column(String(200), comment="工作内容")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    employee = relationship("Employee", back_populates="labor_costs")


class SalesRecord(Base):
    """
    销售记录表
    记录混凝土销售数据，用于利润分析
    """
    __tablename__ = "sales_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    sale_date = Column(Date, index=True, comment="销售日期")
    sale_code = Column(String(50), unique=True, index=True, comment="销售单号")
    customer_name = Column(String(100), comment="客户名称")
    concrete_type = Column(String(50), comment="混凝土强度等级（C30、C40等）")
    quantity = Column(Float, default=0.0, comment="销售数量（立方米）")
    unit_price = Column(Float, default=0.0, comment="单价（元/立方米）")
    total_amount = Column(Float, default=0.0, comment="销售总额（元）")
    delivery_location = Column(String(200), comment="送货地点")
    status = Column(String(20), default="已确认", comment="状态（待确认、已确认、已发货、已收款）")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    profit_analyses = relationship("ProfitAnalysis", back_populates="sales_record")


class ProfitAnalysis(Base):
    """
    利润分析表
    存储单方混凝土毛利分析结果
    """
    __tablename__ = "profit_analyses"
    
    id = Column(Integer, primary_key=True, index=True, comment="分析记录ID")
    analysis_date = Column(Date, index=True, comment="分析日期")
    sales_record_id = Column(Integer, ForeignKey("sales_records.id"), nullable=False, comment="关联销售记录ID")
    concrete_type = Column(String(50), comment="混凝土强度等级")
    
    # 成本分解
    material_cost_per_cubic = Column(Float, default=0.0, comment="单方原材料成本（元/立方米）")
    labor_cost_per_cubic = Column(Float, default=0.0, comment="单方人工成本（元/立方米）")
    energy_cost_per_cubic = Column(Float, default=0.0, comment="单方能耗成本（元/立方米）")
    other_cost_per_cubic = Column(Float, default=0.0, comment="单方其他成本（元/立方米）")
    total_cost_per_cubic = Column(Float, default=0.0, comment="单方总成本（元/立方米）")
    
    # 收入和利润
    sales_price_per_cubic = Column(Float, default=0.0, comment="单方销售价格（元/立方米）")
    gross_profit_per_cubic = Column(Float, default=0.0, comment="单方毛利（元/立方米）")
    gross_profit_margin = Column(Float, default=0.0, comment="毛利率（%）")
    
    # 汇总数据
    total_quantity = Column(Float, default=0.0, comment="总数量（立方米）")
    total_cost = Column(Float, default=0.0, comment="总成本（元）")
    total_sales = Column(Float, default=0.0, comment="总销售额（元）")
    total_gross_profit = Column(Float, default=0.0, comment="总毛利（元）")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系定义
    sales_record = relationship("SalesRecord", back_populates="profit_analyses")
