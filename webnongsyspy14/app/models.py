from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="农产品名称")
    specification = Column(String(50), comment="规格")
    grade = Column(String(20), comment="等级")
    production_date = Column(Date, comment="生产日期")
    shelf_life = Column(Integer, comment="保质期（天）")
    suggested_retail_price = Column(Numeric(10, 2), comment="建议零售价")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    order_items = relationship("OrderItem", back_populates="product")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="客户名称")
    phone = Column(String(20), nullable=False, index=True, comment="联系电话")
    email = Column(String(100), comment="电子邮箱")
    address = Column(String(200), comment="地址")
    contact_person = Column(String(50), comment="联系人")
    preferences = Column(Text, comment="购买偏好")
    status = Column(String(20), default="active", comment="状态: active/inactive")
    created_at = Column(Date, default=date.today)
    updated_at = Column(Date, default=date.today, onupdate=date.today)

    orders = relationship("Order", back_populates="customer")
    purchase_histories = relationship("PurchaseHistory", back_populates="customer")
    feedbacks = relationship("Feedback", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True, comment="客户ID")
    customer_name = Column(String(100), nullable=False, comment="客户名称")
    customer_phone = Column(String(20), nullable=False, comment="客户电话")
    order_date = Column(Date, default=date.today, comment="订单日期")
    total_amount = Column(Numeric(12, 2), nullable=False, comment="订单总金额")
    shipping_status = Column(String(20), default="pending", comment="发货状态: pending/shipped/delivered")
    estimated_delivery_date = Column(Date, comment="预计送达日期")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    contract = relationship("Contract", back_populates="order", uselist=False)
    logistics = relationship("Logistics", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), index=True, comment="产品ID")
    product_name = Column(String(100), comment="产品名称")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    subtotal = Column(Numeric(12, 2), nullable=False, comment="小计")

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, index=True, comment="订单ID")
    contract_number = Column(String(50), unique=True, index=True, comment="合同编号")
    contract_date = Column(Date, comment="合同日期")
    party_a = Column(String(200), comment="甲方")
    party_b = Column(String(200), comment="乙方")
    contract_content = Column(Text, comment="合同内容")
    status = Column(String(20), default="draft", comment="状态: draft/signed/cancelled")
    signed_date = Column(Date, comment="签署日期")
    created_at = Column(Date, default=date.today)

    order = relationship("Order", back_populates="contract")

class Logistics(Base):
    __tablename__ = "logistics"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, index=True, comment="订单ID")
    tracking_number = Column(String(50), unique=True, index=True, comment="物流单号")
    logistics_company = Column(String(100), comment="物流公司")
    current_status = Column(String(50), default="待发货", comment="当前状态")
    current_location = Column(String(200), comment="当前位置")
    estimated_arrival = Column(Date, comment="预计到达时间")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    order = relationship("Order", back_populates="logistics")
    tracks = relationship("LogisticsTrack", back_populates="logistics", cascade="all, delete-orphan")

class LogisticsTrack(Base):
    __tablename__ = "logistics_tracks"

    id = Column(Integer, primary_key=True, index=True)
    logistics_id = Column(Integer, ForeignKey("logistics.id"), index=True, comment="物流ID")
    status = Column(String(50), comment="状态")
    location = Column(String(200), comment="位置")
    description = Column(Text, comment="描述")
    track_time = Column(DateTime, default=datetime.now, comment="时间")

    logistics = relationship("Logistics", back_populates="tracks")

class PurchaseHistory(Base):
    __tablename__ = "purchase_histories"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True, comment="客户ID")
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), index=True, comment="产品ID")
    product_name = Column(String(100), comment="产品名称")
    quantity = Column(Integer, comment="数量")
    unit_price = Column(Numeric(10, 2), comment="单价")
    purchase_date = Column(Date, default=date.today, comment="购买日期")

    customer = relationship("Customer", back_populates="purchase_histories")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True, comment="客户ID")
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=True, comment="订单ID")
    feedback_type = Column(String(20), comment="反馈类型: suggestion/complaint/praise")
    content = Column(Text, nullable=False, comment="反馈内容")
    rating = Column(Integer, comment="评分 1-5")
    feedback_date = Column(Date, default=date.today, comment="反馈日期")
    response = Column(Text, comment="回复")
    status = Column(String(20), default="pending", comment="状态: pending/processing/resolved")
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer", back_populates="feedbacks")
