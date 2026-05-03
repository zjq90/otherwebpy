"""
数据库模型定义模块
使用SQLAlchemy 2.0声明式API定义所有数据表模型
包含: 用户表、商品表、库存表、订单表、黑名单表、活动配置表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy基础模型类"""
    pass


class TimestampMixin:
    """
    时间戳混合类
    为所有模型添加创建时间和更新时间字段
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")


class User(Base, TimestampMixin):
    """
    用户表模型
    
    存储系统用户信息，支持登录认证和权限管理
    """
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_username", "username", unique=True),
        Index("idx_email", "email", unique=True),
        {"comment": "用户表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID(主键)")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名(唯一)")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    email = Column(String(100), unique=True, nullable=True, comment="邮箱地址")
    phone = Column(String(20), nullable=True, comment="手机号")
    is_active = Column(Boolean, default=True, comment="是否激活(0:禁用,1:启用)")
    is_admin = Column(Boolean, default=False, comment="是否管理员(0:普通用户,1:管理员)")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    login_count = Column(Integer, default=0, comment="登录次数")

    # 关系定义
    orders = relationship("Order", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Product(Base, TimestampMixin):
    """
    商品表模型
    
    存储商品基本信息，支持抢单活动商品
    """
    __tablename__ = "products"
    __table_args__ = (
        Index("idx_is_active", "is_active"),
        {"comment": "商品表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="商品ID(主键)")
    product_name = Column(String(200), nullable=False, comment="商品名称")
    product_code = Column(String(50), unique=True, nullable=False, index=True, comment="商品编码(唯一)")
    description = Column(Text, nullable=True, comment="商品描述")
    original_price = Column(Float, nullable=False, comment="原价")
    seckill_price = Column(Float, nullable=False, comment="秒杀价")
    stock_quantity = Column(Integer, nullable=False, default=0, comment="库存数量(数据库)")
    sold_quantity = Column(Integer, nullable=False, default=0, comment="已售数量")
    is_active = Column(Boolean, default=True, index=True, comment="是否上架(0:下架,1:上架)")
    image_url = Column(String(500), nullable=True, comment="商品图片URL")
    category = Column(String(100), nullable=True, comment="商品分类")

    # 关系定义
    inventory = relationship("Inventory", back_populates="product", uselist=False, lazy="select")
    orders = relationship("Order", back_populates="product", lazy="dynamic")

    def __repr__(self):
        return f"<Product(id={self.id}, product_name='{self.product_name}')>"


class Inventory(Base, TimestampMixin):
    """
    库存表模型
    
    独立存储库存信息，便于库存管理和高并发扣减
    """
    __tablename__ = "inventory"
    __table_args__ = (
        Index("idx_product_id", "product_id", unique=True),
        {"comment": "库存表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="库存记录ID(主键)")
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False, index=True, comment="关联商品ID")
    total_stock = Column(Integer, nullable=False, default=0, comment="总库存数量")
    available_stock = Column(Integer, nullable=False, default=0, comment="可用库存数量")
    frozen_stock = Column(Integer, nullable=False, default=0, comment="冻结库存(下单未支付)")
    sold_stock = Column(Integer, nullable=False, default=0, comment="已售库存")
    version = Column(Integer, default=0, comment="乐观锁版本号(用于并发控制)")

    # 关系定义
    product = relationship("Product", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, available={self.available_stock})>"


class Order(Base, TimestampMixin):
    """
    订单表模型
    
    存储订单信息，支持抢单订单处理
    使用订单号作为唯一标识符便于追踪
    """
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_order_no", "order_no", unique=True),
        Index("idx_user_id", "user_id"),
        Index("idx_product_id", "product_id"),
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
        {"comment": "订单表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="订单ID(主键)")
    order_no = Column(String(64), unique=True, nullable=False, index=True, comment="订单编号(唯一)")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True, comment="商品ID")
    product_name = Column(String(200), nullable=False, comment="商品名称(冗余)")
    product_code = Column(String(50), nullable=False, comment="商品编码(冗余)")
    quantity = Column(Integer, nullable=False, default=1, comment="购买数量")
    unit_price = Column(Float, nullable=False, comment="商品单价")
    total_amount = Column(Float, nullable=False, comment="订单总金额")

    # 订单状态: 0-待处理, 1-已确认, 2-已支付, 3-已取消, 4-已退款
    status = Column(Integer, default=0, index=True, comment="订单状态")
    status_message = Column(String(255), nullable=True, comment="状态描述")

    # 支付相关
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    pay_method = Column(String(50), nullable=True, comment="支付方式")
    transaction_id = Column(String(100), nullable=True, comment="第三方交易号")

    # 收货信息
    receiver_name = Column(String(100), nullable=True, comment="收货人姓名")
    receiver_phone = Column(String(20), nullable=True, comment="收货人电话")
    receiver_address = Column(String(500), nullable=True, comment="收货地址")

    # 备注
    remark = Column(Text, nullable=True, comment="订单备注")
    cancel_reason = Column(Text, nullable=True, comment="取消原因")

    # 关系定义
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")

    def __repr__(self):
        return f"<Order(order_no='{self.order_no}', status={self.status})>"


class Blacklist(Base, TimestampMixin):
    """
    黑名单表模型
    
    存储需要拦截的IP或用户ID，用于防止恶意攻击和刷单
    """
    __tablename__ = "blacklist"
    __table_args__ = (
        Index("idx_target", "target_type", "target_value", unique=True),
        Index("idx_is_active", "is_active"),
        Index("idx_expire_at", "expire_at"),
        {"comment": "黑名单表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="黑名单ID(主键)")
    # 目标类型: ip-IP地址, user_id-用户ID
    target_type = Column(String(20), nullable=False, comment="目标类型(ip/user_id)")
    target_value = Column(String(100), nullable=False, comment="目标值(IP地址或用户ID)")
    is_active = Column(Boolean, default=True, index=True, comment="是否有效(0:无效,1:有效)")
    reason = Column(String(500), nullable=True, comment="拉黑原因")
    expire_at = Column(DateTime, nullable=True, index=True, comment="过期时间(Null表示永久)")
    operator_id = Column(Integer, nullable=True, comment="操作人ID")

    def __repr__(self):
        return f"<Blacklist(type={self.target_type}, value='{self.target_value}')>"


class SeckillConfig(Base, TimestampMixin):
    """
    抢单活动配置表模型
    
    存储抢单活动的配置信息，支持多活动管理
    """
    __tablename__ = "seckill_config"
    __table_args__ = (
        Index("idx_product_id", "product_id"),
        Index("idx_is_active", "is_active"),
        {"comment": "抢单活动配置表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="活动配置ID(主键)")
    config_name = Column(String(200), nullable=False, comment="活动配置名称")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True, comment="关联商品ID")
    seckill_stock = Column(Integer, nullable=False, comment="秒杀库存数量")
    start_time = Column(DateTime, nullable=False, comment="活动开始时间")
    end_time = Column(DateTime, nullable=False, comment="活动结束时间")
    is_active = Column(Boolean, default=True, index=True, comment="是否启用(0:禁用,1:启用)")
    max_purchase_per_user = Column(Integer, default=1, comment="每人限购数量")
    # 活动状态标记: 用于Redis预加载时判断活动是否开始
    # 0-未开始, 1-进行中, 2-已结束
    activity_status = Column(Integer, default=0, comment="活动状态")
    # 限流配置
    ip_rate_limit = Column(Integer, default=10, comment="IP每秒限流数")
    user_rate_limit = Column(Integer, default=5, comment="用户每秒限流数")
    global_rate_limit = Column(Integer, default=10000, comment="全局每秒限流数")

    def __repr__(self):
        return f"<SeckillConfig(name='{self.config_name}', product_id={self.product_id})>"
