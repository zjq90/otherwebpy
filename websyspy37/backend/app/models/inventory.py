"""
库存模块数据模型
包含仓库、库存、入库单、出库单等模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base


class Warehouse(Base):
    """
    仓库模型
    存储仓库基本信息
    """
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True, comment="仓库ID")
    warehouse_no = Column(String(50), unique=True, nullable=False, comment="仓库编号")
    name = Column(String(100), nullable=False, comment="仓库名称")
    location = Column(String(255), comment="仓库位置")
    manager = Column(String(50), comment="负责人")
    phone = Column(String(20), comment="联系电话")
    description = Column(Text, comment="仓库描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：一个仓库可以有多个库存记录
    inventories = relationship("Inventory", back_populates="warehouse")
    # 关系：一个仓库可以有多个入库单
    stock_in_orders = relationship("StockInOrder", back_populates="warehouse")
    # 关系：一个仓库可以有多个出库单
    stock_out_orders = relationship("StockOutOrder", back_populates="warehouse")


class Inventory(Base):
    """
    库存模型
    存储库存信息
    """
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True, comment="库存ID")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), comment="仓库ID")
    product_id = Column(Integer, ForeignKey("products.id"), comment="产品ID")
    quantity = Column(Integer, default=0, comment="库存数量")
    min_quantity = Column(Integer, default=0, comment="最低库存预警线")
    max_quantity = Column(Integer, default=10000, comment="最高库存预警线")
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系：库存属于一个仓库
    warehouse = relationship("Warehouse", back_populates="inventories")
    # 关系：库存关联一个产品
    product = relationship("Product", back_populates="inventories")


class StockInOrder(Base):
    """
    入库单模型
    存储入库单信息
    """
    __tablename__ = "stock_in_orders"

    id = Column(Integer, primary_key=True, index=True, comment="入库单ID")
    order_no = Column(String(50), unique=True, nullable=False, comment="入库单编号")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), comment="仓库ID")
    supplier = Column(String(100), comment="供应商")
    order_date = Column(DateTime, default=datetime.now, comment="入库日期")
    total_amount = Column(Float, default=0.0, comment="入库总金额")
    status = Column(String(20), default="待入库", comment="状态：待入库/已入库/已取消")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：入库单属于一个仓库
    warehouse = relationship("Warehouse", back_populates="stock_in_orders")
    # 关系：一个入库单可以有多个入库明细
    stock_in_items = relationship("StockInItem", back_populates="stock_in_order")


class StockInItem(Base):
    """
    入库明细模型
    存储入库单中的商品明细
    """
    __tablename__ = "stock_in_items"

    id = Column(Integer, primary_key=True, index=True, comment="明细ID")
    stock_in_order_id = Column(Integer, ForeignKey("stock_in_orders.id"), comment="入库单ID")
    product_id = Column(Integer, ForeignKey("products.id"), comment="产品ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_price = Column(Float, nullable=False, comment="总价")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系：明细属于一个入库单
    stock_in_order = relationship("StockInOrder", back_populates="stock_in_items")


class StockOutOrder(Base):
    """
    出库单模型
    存储出库单信息
    """
    __tablename__ = "stock_out_orders"

    id = Column(Integer, primary_key=True, index=True, comment="出库单ID")
    order_no = Column(String(50), unique=True, nullable=False, comment="出库单编号")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), comment="仓库ID")
    customer = Column(String(100), comment="客户")
    order_date = Column(DateTime, default=datetime.now, comment="出库日期")
    total_amount = Column(Float, default=0.0, comment="出库总金额")
    status = Column(String(20), default="待出库", comment="状态：待出库/已出库/已取消")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系：出库单属于一个仓库
    warehouse = relationship("Warehouse", back_populates="stock_out_orders")
    # 关系：一个出库单可以有多个出库明细
    stock_out_items = relationship("StockOutItem", back_populates="stock_out_order")


class StockOutItem(Base):
    """
    出库明细模型
    存储出库单中的商品明细
    """
    __tablename__ = "stock_out_items"

    id = Column(Integer, primary_key=True, index=True, comment="明细ID")
    stock_out_order_id = Column(Integer, ForeignKey("stock_out_orders.id"), comment="出库单ID")
    product_id = Column(Integer, ForeignKey("products.id"), comment="产品ID")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_price = Column(Float, nullable=False, comment="总价")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系：明细属于一个出库单
    stock_out_order = relationship("StockOutOrder", back_populates="stock_out_items")
