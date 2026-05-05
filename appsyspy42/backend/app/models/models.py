"""
数据库模型定义
使用SQLAlchemy ORM定义所有数据表结构
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class MaterialType(str, enum.Enum):
    """原材料类型枚举"""
    CEMENT = "水泥"
    SAND = "砂石"
    FLYASH = "粉煤灰"
    ADDITIVE = "外加剂"


class PurchaseStatus(str, enum.Enum):
    """采购申请状态枚举"""
    PENDING = "待审批"
    APPROVED = "已批准"
    REJECTED = "已拒绝"
    COMPLETED = "已完成"


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "管理员"
    PURCHASER = "采购员"


class User(Base):
    """
    用户表
    存储系统用户信息，包括管理员和采购员
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    role = Column(String(20), nullable=False, comment="角色：管理员/采购员")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    is_active = Column(Integer, default=1, comment="是否启用：1启用 0禁用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    purchase_requests = relationship("PurchaseRequest", back_populates="requester")
    approvals = relationship("PurchaseRequest", back_populates="approver", foreign_keys="PurchaseRequest.approved_by")


class Supplier(Base):
    """
    供应商表
    存储供应商基本信息、质量评级等
    """
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True, comment="供应商ID")
    supplier_name = Column(String(100), nullable=False, index=True, comment="供应商名称")
    contact_person = Column(String(50), comment="联系人")
    phone = Column(String(20), comment="联系电话")
    address = Column(String(200), comment="地址")
    business_license = Column(String(100), comment="营业执照号")
    quality_rating = Column(Float, default=5.0, comment="质量评级（1-5分）")
    total_orders = Column(Integer, default=0, comment="总订单数")
    total_amount = Column(Float, default=0.0, comment="总交易金额")
    description = Column(Text, comment="供应商描述")
    is_active = Column(Integer, default=1, comment="是否启用：1启用 0禁用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    supply_records = relationship("SupplyRecord", back_populates="supplier")
    evaluations = relationship("SupplierEvaluation", back_populates="supplier")


class Material(Base):
    """
    原材料表
    存储原材料基本信息，包括类型、规格等
    """
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True, comment="原材料ID")
    material_name = Column(String(100), nullable=False, index=True, comment="原材料名称")
    material_type = Column(String(20), nullable=False, index=True, comment="类型：水泥/砂石/粉煤灰/外加剂")
    specification = Column(String(100), comment="规格型号")
    unit = Column(String(20), default="吨", comment="计量单位")
    description = Column(Text, comment="描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    inventory = relationship("Inventory", back_populates="material")
    purchase_requests = relationship("PurchaseRequest", back_populates="material")
    supply_records = relationship("SupplyRecord", back_populates="material")


class Warehouse(Base):
    """
    料仓表
    存储料仓信息，包括位置、容量等
    """
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True, comment="料仓ID")
    warehouse_name = Column(String(100), nullable=False, comment="料仓名称")
    location = Column(String(200), comment="位置")
    max_capacity = Column(Float, nullable=False, comment="最大容量")
    current_usage = Column(Float, default=0, comment="当前使用量")
    description = Column(Text, comment="描述")
    is_active = Column(Integer, default=1, comment="是否启用：1启用 0禁用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    inventory = relationship("Inventory", back_populates="warehouse")


class Inventory(Base):
    """
    库存表
    存储实时库存信息，包括余量、料仓、保质期等
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, comment="库存ID")
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True, comment="原材料ID")
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True, comment="料仓ID")
    quantity = Column(Float, default=0, comment="当前库存数量")
    safety_threshold = Column(Float, default=100, comment="安全阈值，低于此值触发预警")
    unit_price = Column(Float, comment="单价")
    production_date = Column(DateTime, comment="生产日期")
    expiry_date = Column(DateTime, comment="保质期/到期日期")
    batch_number = Column(String(100), comment="批次号")
    is_low_stock = Column(Integer, default=0, comment="是否低库存：1是 0否")
    last_check_time = Column(DateTime, comment="上次盘点时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    material = relationship("Material", back_populates="inventory")
    warehouse = relationship("Warehouse", back_populates="inventory")
    alerts = relationship("StockAlert", back_populates="inventory")


class PurchaseRequest(Base):
    """
    采购申请表
    存储采购申请信息，支持审批流程
    """
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True, comment="采购申请ID")
    request_no = Column(String(50), unique=True, nullable=False, index=True, comment="申请单号")
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True, comment="原材料ID")
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="申请人ID")
    quantity = Column(Float, nullable=False, comment="需求数量")
    unit = Column(String(20), default="吨", comment="单位")
    expected_delivery_date = Column(DateTime, comment="预计到货时间")
    status = Column(String(20), default="待审批", comment="状态：待审批/已批准/已拒绝/已完成")
    reason = Column(Text, comment="申请原因")
    approved_by = Column(Integer, ForeignKey("users.id"), comment="审批人ID")
    approval_time = Column(DateTime, comment="审批时间")
    approval_comment = Column(Text, comment="审批意见")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    material = relationship("Material", back_populates="purchase_requests")
    requester = relationship("User", back_populates="purchase_requests", foreign_keys=[requested_by])
    approver = relationship("User", back_populates="approvals", foreign_keys=[approved_by])


class SupplyRecord(Base):
    """
    供货记录表
    存储供应商历史供货记录
    """
    __tablename__ = "supply_records"

    id = Column(Integer, primary_key=True, index=True, comment="供货记录ID")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True, comment="供应商ID")
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False, index=True, comment="原材料ID")
    quantity = Column(Float, nullable=False, comment="供货数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    total_amount = Column(Float, comment="总金额")
    delivery_date = Column(DateTime, comment="送货日期")
    quality_status = Column(String(20), default="合格", comment="质量状态：合格/不合格/待检验")
    batch_number = Column(String(100), comment="批次号")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    supplier = relationship("Supplier", back_populates="supply_records")
    material = relationship("Material", back_populates="supply_records")


class SupplierEvaluation(Base):
    """
    供应商评价表
    存储对供应商的评价打分
    """
    __tablename__ = "supplier_evaluations"

    id = Column(Integer, primary_key=True, index=True, comment="评价ID")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True, comment="供应商ID")
    evaluated_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评价人ID")
    quality_score = Column(Float, default=5.0, comment="质量评分（1-5分）")
    delivery_score = Column(Float, default=5.0, comment="交货及时性评分（1-5分）")
    price_score = Column(Float, default=5.0, comment="价格合理性评分（1-5分）")
    service_score = Column(Float, default=5.0, comment="服务态度评分（1-5分）")
    total_score = Column(Float, default=5.0, comment="综合评分")
    comment = Column(Text, comment="评价内容")
    evaluation_date = Column(DateTime, default=datetime.now, comment="评价日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    supplier = relationship("Supplier", back_populates="evaluations")


class StockAlert(Base):
    """
    库存预警表
    存储库存低于安全阈值时的预警记录
    """
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True, index=True, comment="预警ID")
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False, index=True, comment="库存ID")
    alert_type = Column(String(20), default="低库存", comment="预警类型：低库存/即将过期")
    threshold_value = Column(Float, comment="阈值")
    current_value = Column(Float, comment="当前值")
    message = Column(Text, comment="预警消息")
    is_read = Column(Integer, default=0, comment="是否已读：1是 0否")
    is_handled = Column(Integer, default=0, comment="是否已处理：1是 0否")
    handled_by = Column(Integer, ForeignKey("users.id"), comment="处理人ID")
    handled_at = Column(DateTime, comment="处理时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    inventory = relationship("Inventory", back_populates="alerts")
