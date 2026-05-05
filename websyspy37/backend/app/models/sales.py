"""
销售模块数据模型
包含客户、订单、订单明细等模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base


class Customer(Base):
    """
    客户模型
    存储客户基本信息
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, comment="客户ID")
    name = Column(String(100), nullable=False, comment="客户名称")
    contact_person = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    address = Column(String(255), comment="地址")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个客户可以有多个订单
    orders = relationship("Order", back_populates="customer")


class Order(Base):
    """
    订单模型
    存储订单基本信息
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, comment="订单ID")
    order_no = Column(String(50), unique=True, nullable=False, comment="订单编号")
    customer_id = Column(Integer, ForeignKey("customers.id"), comment="客户ID")
    order_date = Column(DateTime, default=datetime.now, comment="订单日期")
    total_amount = Column(Float, default=0.0, comment="订单总金额")
    status = Column(String(20), default="待处理", comment="订单状态：待处理/已确认/已发货/已完成/已取消")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：订单属于一个客户
    customer = relationship("Customer", back_populates="orders")
    # 关系：一个订单可以有多个订单明细
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    订单明细模型
    存储订单中的商品明细
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, comment="明细ID")
    order_id = Column(Integer, ForeignKey("orders.id"), comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), comment="产品ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_price = Column(Float, nullable=False, comment="总价")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系：明细属于一个订单
    order = relationship("Order", back_populates="order_items")
    # 关系：明细关联一个产品
    product = relationship("Product", back_populates="order_items")
