"""
数据库模型定义
使用SQLAlchemy ORM定义所有数据表结构
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Supplier(Base):
    """
    供应商表
    记录种子、肥料、农药、农膜等物资的供应商信息
    """
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True, comment="供应商ID")
    name = Column(String(100), nullable=False, comment="供应商名称")
    contact_person = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    address = Column(String(200), comment="地址")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联采购记录
    purchases = relationship("Purchase", back_populates="supplier")


class Category(Base):
    """
    农资分类表
    种子、肥料、农药、农膜等分类
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True, comment="分类ID")
    name = Column(String(50), nullable=False, unique=True, comment="分类名称")
    code = Column(String(20), nullable=False, unique=True, comment="分类编码")
    description = Column(Text, comment="分类描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联农资
    supplies = relationship("Supply", back_populates="category")


class Supply(Base):
    """
    农资表
    记录种子、肥料、农药、农膜等农资的基本信息
    """
    __tablename__ = "supplies"
    
    id = Column(Integer, primary_key=True, index=True, comment="农资ID")
    name = Column(String(100), nullable=False, comment="农资名称")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, comment="分类ID")
    unit = Column(String(20), comment="单位（袋/瓶/公斤等）")
    specification = Column(String(100), comment="规格")
    brand = Column(String(50), comment="品牌")
    warning_threshold = Column(Float, default=10.0, comment="库存预警阈值（数量）")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    category = relationship("Category", back_populates="supplies")
    purchases = relationship("Purchase", back_populates="supply")
    inventory_items = relationship("Inventory", back_populates="supply")
    usage_records = relationship("UsageRecord", back_populates="supply")


class Plot(Base):
    """
    地块表
    记录农田地块信息
    """
    __tablename__ = "plots"
    
    id = Column(Integer, primary_key=True, index=True, comment="地块ID")
    name = Column(String(100), nullable=False, comment="地块名称")
    location = Column(String(200), comment="位置")
    area = Column(Float, comment="面积（亩）")
    soil_type = Column(String(50), comment="土壤类型")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联使用记录
    usage_records = relationship("UsageRecord", back_populates="plot")


class Crop(Base):
    """
    作物表
    记录种植的作物信息
    """
    __tablename__ = "crops"
    
    id = Column(Integer, primary_key=True, index=True, comment="作物ID")
    name = Column(String(100), nullable=False, comment="作物名称")
    variety = Column(String(100), comment="品种")
    growth_cycle = Column(Integer, comment="生长周期（天）")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联使用记录
    usage_records = relationship("UsageRecord", back_populates="crop")


class Purchase(Base):
    """
    采购记录表
    记录采购信息，关联供应商、农资
    """
    __tablename__ = "purchases"
    
    id = Column(Integer, primary_key=True, index=True, comment="采购ID")
    purchase_no = Column(String(50), unique=True, nullable=False, comment="采购单号")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, comment="供应商ID")
    supply_id = Column(Integer, ForeignKey("supplies.id"), nullable=False, comment="农资ID")
    purchase_date = Column(Date, nullable=False, comment="采购日期")
    quantity = Column(Float, nullable=False, comment="采购数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_price = Column(Float, comment="总价")
    batch_no = Column(String(50), nullable=False, comment="批次号")
    expiry_date = Column(Date, comment="保质期")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    supplier = relationship("Supplier", back_populates="purchases")
    supply = relationship("Supply", back_populates="purchases")
    inventory_items = relationship("Inventory", back_populates="purchase")


class Inventory(Base):
    """
    库存表
    实时更新库存数量，支持批次管理，确保先进先出
    """
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True, comment="库存ID")
    supply_id = Column(Integer, ForeignKey("supplies.id"), nullable=False, comment="农资ID")
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False, comment="采购ID")
    batch_no = Column(String(50), nullable=False, comment="批次号")
    quantity = Column(Float, nullable=False, default=0, comment="库存数量")
    expiry_date = Column(Date, comment="保质期")
    is_expired = Column(Boolean, default=False, comment="是否过期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    supply = relationship("Supply", back_populates="inventory_items")
    purchase = relationship("Purchase", back_populates="inventory_items")
    usage_records = relationship("UsageRecord", back_populates="inventory")


class UsageRecord(Base):
    """
    使用记录表
    关联地块与作物，记录每项农资的实际使用情况
    形成"投入品-地块-作物"闭环
    """
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="使用记录ID")
    usage_date = Column(Date, nullable=False, comment="使用日期")
    supply_id = Column(Integer, ForeignKey("supplies.id"), nullable=False, comment="农资ID")
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False, comment="库存ID")
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=False, comment="地块ID")
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, comment="作物ID")
    quantity = Column(Float, nullable=False, comment="使用数量")
    usage_method = Column(String(100), comment="使用方法")
    operator = Column(String(50), comment="操作人")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    supply = relationship("Supply", back_populates="usage_records")
    inventory = relationship("Inventory", back_populates="usage_records")
    plot = relationship("Plot", back_populates="usage_records")
    crop = relationship("Crop", back_populates="usage_records")
