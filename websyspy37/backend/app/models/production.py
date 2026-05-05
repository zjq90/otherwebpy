"""
生产模块数据模型
包含产品、生产计划、生产任务等模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base


class Product(Base):
    """
    产品模型
    存储产品基本信息
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    product_no = Column(String(50), unique=True, nullable=False, comment="产品编号")
    name = Column(String(100), nullable=False, comment="产品名称")
    specification = Column(String(100), comment="规格型号")
    unit = Column(String(20), default="个", comment="单位")
    cost_price = Column(Float, default=0.0, comment="成本价")
    selling_price = Column(Float, default=0.0, comment="销售价")
    description = Column(Text, comment="产品描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个产品可以出现在多个订单明细中
    order_items = relationship("OrderItem", back_populates="product")
    # 关系：一个产品可以有多个库存记录
    inventories = relationship("Inventory", back_populates="product")
    # 关系：一个产品可以出现在多个生产任务中
    production_tasks = relationship("ProductionTask", back_populates="product")


class ProductionPlan(Base):
    """
    生产计划模型
    存储生产计划信息
    """
    __tablename__ = "production_plans"

    id = Column(Integer, primary_key=True, index=True, comment="计划ID")
    plan_no = Column(String(50), unique=True, nullable=False, comment="计划编号")
    name = Column(String(100), nullable=False, comment="计划名称")
    start_date = Column(DateTime, comment="开始日期")
    end_date = Column(DateTime, comment="结束日期")
    status = Column(String(20), default="待执行", comment="计划状态：待执行/执行中/已完成/已取消")
    description = Column(Text, comment="计划描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个计划可以有多个生产任务
    production_tasks = relationship("ProductionTask", back_populates="production_plan")


class ProductionTask(Base):
    """
    生产任务模型
    存储生产任务信息
    """
    __tablename__ = "production_tasks"

    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    task_no = Column(String(50), unique=True, nullable=False, comment="任务编号")
    plan_id = Column(Integer, ForeignKey("production_plans.id"), comment="生产计划ID")
    product_id = Column(Integer, ForeignKey("products.id"), comment="产品ID")
    quantity = Column(Integer, nullable=False, comment="生产数量")
    start_date = Column(DateTime, comment="开始日期")
    end_date = Column(DateTime, comment="结束日期")
    actual_quantity = Column(Integer, default=0, comment="实际完成数量")
    status = Column(String(20), default="待处理", comment="任务状态：待处理/进行中/已完成/已取消")
    description = Column(Text, comment="任务描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：任务属于一个生产计划
    production_plan = relationship("ProductionPlan", back_populates="production_tasks")
    # 关系：任务关联一个产品
    product = relationship("Product", back_populates="production_tasks")
