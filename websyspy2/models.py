"""
数据库模型定义文件
包含所有数据表的ORM模型定义
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    用户表模型
    存储系统用户信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    real_name = Column(String(50), comment="真实姓名")
    email = Column(String(100), comment="电子邮箱")
    phone = Column(String(20), comment="联系电话")
    role = Column(String(20), default="user", comment="角色：admin-管理员，user-普通用户")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：用户创建的进销存记录
    inventory_records = relationship("InventoryRecord", back_populates="operator")


class Category(Base):
    """
    产品分类表模型
    存储产品分类信息，支持多级分类
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, comment="分类ID")
    name = Column(String(100), nullable=False, comment="分类名称")
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, comment="父分类ID")
    description = Column(Text, comment="分类描述")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：子分类
    children = relationship("Category", backref="parent", remote_side=[id])
    # 关系：该分类下的产品
    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    产品表模型
    存储产品信息
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, comment="产品ID")
    name = Column(String(200), nullable=False, comment="产品名称")
    code = Column(String(50), unique=True, index=True, comment="产品编码")
    category_id = Column(Integer, ForeignKey("categories.id"), comment="分类ID")
    description = Column(Text, comment="产品描述")
    specification = Column(String(200), comment="产品规格")
    unit = Column(String(20), comment="计量单位")
    cost_price = Column(Numeric(10, 2), default=0.00, comment="成本价")
    selling_price = Column(Numeric(10, 2), default=0.00, comment="销售价")
    stock_quantity = Column(Integer, default=0, comment="库存数量")
    min_stock = Column(Integer, default=0, comment="最低库存预警")
    max_stock = Column(Integer, default=99999, comment="最高库存")
    image = Column(String(500), comment="产品图片路径")
    status = Column(Integer, default=1, comment="状态：1-上架，0-下架")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：所属分类
    category = relationship("Category", back_populates="products")
    # 关系：进销存记录
    inventory_records = relationship("InventoryRecord", back_populates="product")


class InventoryRecord(Base):
    """
    进销存记录表模型
    存储入库和出库记录
    """
    __tablename__ = "inventory_records"

    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="产品ID")
    record_type = Column(String(10), nullable=False, comment="类型：in-入库，out-出库")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), default=0.00, comment="单价")
    total_amount = Column(Numeric(10, 2), default=0.00, comment="总金额")
    operator_id = Column(Integer, ForeignKey("users.id"), comment="操作人ID")
    remark = Column(Text, comment="备注")
    reference_no = Column(String(50), comment="参考单号（如订单号、采购单号等）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系：关联的产品
    product = relationship("Product", back_populates="inventory_records")
    # 关系：操作人
    operator = relationship("User", back_populates="inventory_records")
