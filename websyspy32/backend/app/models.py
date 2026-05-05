from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Silo(Base):
    __tablename__ = "silos"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="料仓名称，如：水泥仓1号、砂石仓等")
    material_type = Column(String(50), nullable=False, comment="物料类型：水泥、砂石、粉煤灰、外加剂等")
    capacity = Column(Float, nullable=False, comment="料仓最大容量(吨)")
    current_level = Column(Float, nullable=False, default=0.0, comment="当前剩余量(吨)")
    min_threshold = Column(Float, nullable=False, default=10.0, comment="低库存预警阈值(吨)")
    unit = Column(String(20), default="吨", comment="计量单位")
    status = Column(String(20), default="正常", comment="状态：正常/低库存/空仓")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    inventory_records = relationship("InventoryRecord", back_populates="silo")

class InventoryRecord(Base):
    __tablename__ = "inventory_records"
    
    id = Column(Integer, primary_key=True, index=True)
    silo_id = Column(Integer, ForeignKey("silos.id"), nullable=False)
    change_type = Column(String(20), nullable=False, comment="变更类型：入库/出库/调整")
    quantity = Column(Float, nullable=False, comment="变更数量(吨)")
    balance_before = Column(Float, nullable=False, comment="变更前库存")
    balance_after = Column(Float, nullable=False, comment="变更后库存")
    reason = Column(String(200), comment="变更原因")
    operator = Column(String(50), comment="操作人")
    record_time = Column(DateTime, default=datetime.now)
    
    silo = relationship("Silo", back_populates="inventory_records")

class ProductionPlan(Base):
    __tablename__ = "production_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(100), nullable=False, comment="生产计划名称")
    plan_date = Column(Date, nullable=False, comment="计划日期")
    concrete_volume = Column(Float, nullable=False, comment="计划生产混凝土方量(立方米)")
    concrete_grade = Column(String(50), comment="混凝土标号，如C30、C50等")
    status = Column(String(20), default="待执行", comment="状态：待执行/执行中/已完成/已取消")
    description = Column(Text, comment="计划描述")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    material_demands = relationship("MaterialDemand", back_populates="production_plan")

class MaterialDemand(Base):
    __tablename__ = "material_demands"
    
    id = Column(Integer, primary_key=True, index=True)
    production_plan_id = Column(Integer, ForeignKey("production_plans.id"), nullable=False)
    material_type = Column(String(50), nullable=False, comment="物料类型：水泥、砂石、粉煤灰、外加剂等")
    required_quantity = Column(Float, nullable=False, comment="预测需求量(吨)")
    unit_consumption = Column(Float, nullable=False, comment="单位消耗量(吨/立方米)")
    current_stock = Column(Float, default=0.0, comment="当前库存(吨)")
    shortage = Column(Float, default=0.0, comment="缺口量(吨)")
    priority = Column(Integer, default=1, comment="优先级：1-紧急、2-高、3-中、4-低")
    status = Column(String(20), default="待处理", comment="状态：待处理/已补货/部分补货/已满足")
    created_at = Column(DateTime, default=datetime.now)
    
    production_plan = relationship("ProductionPlan", back_populates="material_demands")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="供应商名称")
    contact_person = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    address = Column(String(200), comment="地址")
    material_types = Column(String(200), comment="供应物料类型，多个用逗号分隔")
    overall_rating = Column(Float, default=5.0, comment="综合评分(1-10分)")
    status = Column(String(20), default="合作中", comment="状态：合作中/暂停合作/已终止")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    ratings = relationship("SupplierRating", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class SupplierRating(Base):
    __tablename__ = "supplier_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    rating_date = Column(Date, nullable=False, comment="评分日期")
    delivery_score = Column(Float, nullable=False, comment="供货及时性评分(1-10分)")
    quality_score = Column(Float, nullable=False, comment="材料质量评分(1-10分)")
    price_score = Column(Float, default=7.0, comment="价格合理性评分(1-10分)")
    service_score = Column(Float, default=7.0, comment="服务态度评分(1-10分)")
    total_score = Column(Float, comment="综合评分")
    comment = Column(Text, comment="评价备注")
    evaluator = Column(String(50), comment="评价人")
    created_at = Column(DateTime, default=datetime.now)
    
    supplier = relationship("Supplier", back_populates="ratings")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, comment="采购订单编号")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    material_type = Column(String(50), nullable=False, comment="物料类型")
    quantity = Column(Float, nullable=False, comment="采购数量(吨)")
    unit_price = Column(Float, nullable=False, comment="单价(元/吨)")
    total_amount = Column(Float, nullable=False, comment="总金额(元)")
    order_date = Column(Date, nullable=False, comment="下单日期")
    delivery_date = Column(Date, comment="约定交货日期")
    actual_delivery_date = Column(Date, comment="实际交货日期")
    status = Column(String(20), default="待发货", comment="状态：待发货/已发货/部分收货/已完成/已取消")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    supplier = relationship("Supplier", back_populates="purchase_orders")
    settlement = relationship("Settlement", back_populates="purchase_order", uselist=False)

class Settlement(Base):
    __tablename__ = "settlements"
    
    id = Column(Integer, primary_key=True, index=True)
    settlement_no = Column(String(50), unique=True, nullable=False, comment="结算单编号")
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    settlement_date = Column(Date, nullable=False, comment="结算日期")
    material_type = Column(String(50), nullable=False, comment="物料类型")
    quantity = Column(Float, nullable=False, comment="结算数量(吨)")
    unit_price = Column(Float, nullable=False, comment="单价(元/吨)")
    total_amount = Column(Float, nullable=False, comment="结算金额(元)")
    tax_rate = Column(Float, default=0.13, comment="税率")
    tax_amount = Column(Float, default=0.0, comment="税额")
    total_payable = Column(Float, default=0.0, comment="应付总额(含税)")
    payment_status = Column(String(20), default="待付款", comment="付款状态：待付款/部分付款/已付款")
    paid_amount = Column(Float, default=0.0, comment="已付金额(元)")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now)
    
    purchase_order = relationship("PurchaseOrder", back_populates="settlement")
