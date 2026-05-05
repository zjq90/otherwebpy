"""
数据库模型模块
定义所有数据库表的ORM模型
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """
    用户模型
    存储用户基本信息
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password = Column(String(255))
    nickname = Column(String(50))
    avatar = Column(String(255))
    email = Column(String(100))
    gender = Column(Integer, default=0)  # 0: 未知, 1: 男, 2: 女
    register_time = Column(DateTime, default=datetime.now)
    last_login_time = Column(DateTime)
    status = Column(Integer, default=1)  # 0: 禁用, 1: 正常
    
    # 积分和统计信息
    points = Column(Integer, default=0)  # 积分余额
    total_points = Column(Integer, default=0)  # 累计积分
    recycle_count = Column(Integer, default=0)  # 回收次数
    carbon_reduction = Column(Float, default=0.0)  # 累计减碳量(kg)
    
    # 邀请相关
    invite_code = Column(String(20), unique=True, index=True)  # 邀请码
    invited_by = Column(Integer)  # 被谁邀请
    
    # 关系
    addresses = relationship("UserAddress", back_populates="user")
    recycle_orders = relationship("RecycleOrder", back_populates="user")
    exchange_orders = relationship("ExchangeOrder", back_populates="user")
    points_transactions = relationship("PointsTransaction", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    login_methods = relationship("LoginMethod", back_populates="user")
    
    def to_dict(self):
        return {
            "id": self.id,
            "phone": self.phone,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "email": self.email,
            "gender": self.gender,
            "register_time": self.register_time.isoformat() if self.register_time else None,
            "last_login_time": self.last_login_time.isoformat() if self.last_login_time else None,
            "status": self.status,
            "points": self.points,
            "total_points": self.total_points,
            "recycle_count": self.recycle_count,
            "carbon_reduction": self.carbon_reduction,
            "invite_code": self.invite_code,
            "invited_by": self.invited_by,
        }


class LoginMethod(Base):
    """
    登录方式模型
    支持手机号、微信、支付宝等多种登录方式
    """
    __tablename__ = "login_methods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_type = Column(String(20), nullable=False)  # phone, wechat, alipay
    openid = Column(String(100))  # 第三方登录的唯一标识
    unionid = Column(String(100))
    extra_info = Column(Text)  # 额外信息(JSON)
    create_time = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="login_methods")
    
    __table_args__ = (
        UniqueConstraint('login_type', 'openid', name='uq_login_type_openid'),
    )


class UserAddress(Base):
    """
    用户收货地址模型
    """
    __tablename__ = "user_addresses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)  # 收货人姓名
    phone = Column(String(20), nullable=False)  # 收货人电话
    province = Column(String(50))
    city = Column(String(50))
    district = Column(String(50))
    address = Column(String(255), nullable=False)  # 详细地址
    is_default = Column(Integer, default=0)  # 是否默认地址
    status = Column(Integer, default=1)  # 0: 已删除, 1: 正常
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="addresses")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "address": self.address,
            "full_address": f"{self.province or ''}{self.city or ''}{self.district or ''}{self.address}",
            "is_default": self.is_default,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class ClothingType(Base):
    """
    衣物类型模型
    定义可回收的衣物类型
    """
    __tablename__ = "clothing_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # 类型名称，如T恤、毛衣、羽绒服
    code = Column(String(50), unique=True, nullable=False)  # 类型代码
    description = Column(Text)  # 描述
    icon = Column(String(255))  # 图标
    points_per_unit = Column(Integer, default=10)  # 每件积分
    carbon_per_unit = Column(Float, default=0.5)  # 每件减碳量(kg)
    sort_order = Column(Integer, default=0)  # 排序
    status = Column(Integer, default=1)  # 0: 禁用, 1: 启用
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "icon": self.icon,
            "points_per_unit": self.points_per_unit,
            "carbon_per_unit": self.carbon_per_unit,
            "sort_order": self.sort_order,
        }


class Collector(Base):
    """
    回收人员模型
    """
    __tablename__ = "collectors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # 关联用户表，如果回收员也是用户
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    avatar = Column(String(255))
    id_card = Column(String(50))  # 身份证号
    work_status = Column(Integer, default=0)  # 0: 休息, 1: 工作中, 2: 忙碌
    latitude = Column(Float)  # 当前纬度
    longitude = Column(Float)  # 当前经度
    location_update_time = Column(DateTime)  # 位置更新时间
    rating = Column(Float, default=5.0)  # 评分
    total_orders = Column(Integer, default=0)  # 完成订单数
    status = Column(Integer, default=1)  # 0: 禁用, 1: 正常
    create_time = Column(DateTime, default=datetime.now)
    
    # 关系
    recycle_orders = relationship("RecycleOrder", back_populates="collector")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "avatar": self.avatar,
            "work_status": self.work_status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rating": self.rating,
            "total_orders": self.total_orders,
        }


class RecycleOrder(Base):
    """
    回收订单模型
    """
    __tablename__ = "recycle_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True)  # 订单号
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    collector_id = Column(Integer, ForeignKey("collectors.id"), index=True)  # 回收员ID
    
    # 衣物信息
    clothing_type_id = Column(Integer, ForeignKey("clothing_types.id"), nullable=False)
    clothing_name = Column(String(50))  # 衣物类型名称（冗余）
    quantity = Column(Integer, nullable=False)  # 数量
    unit = Column(String(20), default="件")  # 单位
    quality = Column(String(20), default="普通")  # 品质：优质、普通、较差
    
    # 地址信息
    province = Column(String(50))
    city = Column(String(50))
    district = Column(String(50))
    address = Column(String(255), nullable=False)  # 详细地址
    contact_name = Column(String(50), nullable=False)  # 联系人
    contact_phone = Column(String(20), nullable=False)  # 联系电话
    
    # 时间信息
    scheduled_date = Column(String(20), nullable=False)  # 预约日期
    scheduled_time_slot = Column(String(50), nullable=False)  # 预约时间段
    estimated_arrival = Column(String(50))  # 预计上门时段
    actual_arrival_time = Column(DateTime)  # 实际上门时间
    complete_time = Column(DateTime)  # 完成时间
    cancel_time = Column(DateTime)  # 取消时间
    cancel_reason = Column(Text)  # 取消原因
    
    # 状态和积分
    status = Column(Integer, default=1, index=True)  # 1:待接单, 2:待上门, 3:回收中, 4:已完成, 5:已取消
    status_text = Column(String(50), default="待接单")
    points_earned = Column(Integer, default=0)  # 获得的积分
    carbon_earned = Column(Float, default=0.0)  # 获得的减碳量
    
    remark = Column(Text)  # 备注
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="recycle_orders")
    collector = relationship("Collector", back_populates="recycle_orders")
    status_histories = relationship("OrderStatusHistory", back_populates="order")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "user_id": self.user_id,
            "collector_id": self.collector_id,
            "clothing_type_id": self.clothing_type_id,
            "clothing_name": self.clothing_name,
            "quantity": self.quantity,
            "unit": self.unit,
            "quality": self.quality,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "address": self.address,
            "full_address": f"{self.province or ''}{self.city or ''}{self.district or ''}{self.address}",
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "scheduled_date": self.scheduled_date,
            "scheduled_time_slot": self.scheduled_time_slot,
            "estimated_arrival": self.estimated_arrival,
            "status": self.status,
            "status_text": self.status_text,
            "points_earned": self.points_earned,
            "carbon_earned": self.carbon_earned,
            "remark": self.remark,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }


class OrderStatusHistory(Base):
    """
    订单状态历史模型
    记录订单状态变更历史
    """
    __tablename__ = "order_status_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("recycle_orders.id"), nullable=False)
    order_no = Column(String(50))
    status = Column(Integer, nullable=False)  # 状态值
    status_text = Column(String(50))  # 状态文本
    operator_type = Column(String(20))  # 操作者类型：user, collector, system
    operator_id = Column(Integer)  # 操作者ID
    remark = Column(Text)  # 备注
    create_time = Column(DateTime, default=datetime.now)
    
    # 关系
    order = relationship("RecycleOrder", back_populates="status_histories")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "order_no": self.order_no,
            "status": self.status,
            "status_text": self.status_text,
            "operator_type": self.operator_type,
            "operator_id": self.operator_id,
            "remark": self.remark,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class PointsConfig(Base):
    """
    积分配置模型
    """
    __tablename__ = "points_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False)  # 配置键
    config_value = Column(String(255), nullable=False)  # 配置值
    description = Column(Text)  # 描述
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PointsTransaction(Base):
    """
    积分交易记录模型
    """
    __tablename__ = "points_transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)  # 类型：recycle(回收), invite(邀请), exchange(兑换), adjust(调整)
    transaction_type_text = Column(String(50))
    points = Column(Integer, nullable=False)  # 积分数量（正为增加，负为减少）
    balance_after = Column(Integer, nullable=False)  # 变动后余额
    reference_type = Column(String(50))  # 关联类型：order, exchange_order, invite
    reference_id = Column(Integer)  # 关联ID
    description = Column(Text)  # 描述
    create_time = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="points_transactions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "transaction_type": self.transaction_type,
            "transaction_type_text": self.transaction_type_text,
            "points": self.points,
            "balance_after": self.balance_after,
            "reference_type": self.reference_type,
            "reference_id": self.reference_id,
            "description": self.description,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class Invite(Base):
    """
    邀请记录模型
    """
    __tablename__ = "invites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 邀请人ID
    invitee_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)  # 被邀请人ID
    invite_code = Column(String(20))  # 使用的邀请码
    inviter_points_earned = Column(Integer, default=0)  # 邀请人获得的积分
    invitee_points_earned = Column(Integer, default=0)  # 被邀请人获得的积分
    status = Column(Integer, default=0)  # 0: 待确认, 1: 已确认, 2: 已发放积分
    create_time = Column(DateTime, default=datetime.now)


class ProductCategory(Base):
    """
    商品分类模型
    """
    __tablename__ = "product_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True)
    icon = Column(String(255))
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "icon": self.icon,
            "sort_order": self.sort_order,
        }


class Product(Base):
    """
    商品模型
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 商品名称
    code = Column(String(50), unique=True)  # 商品编码
    description = Column(Text)  # 描述
    image = Column(String(255))  # 主图
    images = Column(Text)  # 轮播图(JSON数组)
    category_id = Column(Integer, ForeignKey("product_categories.id"))  # 分类ID
    price = Column(Float, default=0.0)  # 现金价格
    points_price = Column(Integer, default=0)  # 积分价格
    exchange_type = Column(String(20), default="points")  # 兑换类型：points(纯积分), points_cash(积分+现金), clothing(旧衣兑换)
    required_clothing_quantity = Column(Integer, default=0)  # 所需旧衣数量
    stock = Column(Integer, default=0)  # 库存
    sales = Column(Integer, default=0)  # 销量
    sort_order = Column(Integer, default=0)  # 排序
    is_hot = Column(Integer, default=0)  # 是否热门
    is_new = Column(Integer, default=0)  # 是否新品
    status = Column(Integer, default=1)  # 0: 下架, 1: 上架
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "image": self.image,
            "images": self.images,
            "category_id": self.category_id,
            "price": self.price,
            "points_price": self.points_price,
            "exchange_type": self.exchange_type,
            "required_clothing_quantity": self.required_clothing_quantity,
            "stock": self.stock,
            "sales": self.sales,
            "is_hot": self.is_hot,
            "is_new": self.is_new,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class ExchangeOrder(Base):
    """
    兑换订单模型
    """
    __tablename__ = "exchange_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(100))  # 商品名称（冗余）
    product_image = Column(String(255))  # 商品图片（冗余）
    quantity = Column(Integer, default=1)  # 数量
    exchange_type = Column(String(20))  # 兑换类型
    points_spent = Column(Integer, default=0)  # 消耗积分
    cash_spent = Column(Float, default=0.0)  # 支付现金
    clothing_spent = Column(Integer, default=0)  # 消耗旧衣数量
    
    # 收货地址信息
    receiver_name = Column(String(50))
    receiver_phone = Column(String(20))
    receiver_province = Column(String(50))
    receiver_city = Column(String(50))
    receiver_district = Column(String(50))
    receiver_address = Column(String(255))
    
    # 物流信息
    express_company = Column(String(50))
    express_no = Column(String(50))
    
    # 订单状态
    status = Column(Integer, default=1)  # 1:待发货, 2:已发货, 3:已签收, 4:已取消
    status_text = Column(String(50), default="待发货")
    remark = Column(Text)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="exchange_orders")
    
    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_image": self.product_image,
            "quantity": self.quantity,
            "exchange_type": self.exchange_type,
            "points_spent": self.points_spent,
            "cash_spent": self.cash_spent,
            "receiver_name": self.receiver_name,
            "receiver_phone": self.receiver_phone,
            "receiver_province": self.receiver_province,
            "receiver_city": self.receiver_city,
            "receiver_district": self.receiver_district,
            "receiver_address": self.receiver_address,
            "express_company": self.express_company,
            "express_no": self.express_no,
            "status": self.status,
            "status_text": self.status_text,
            "remark": self.remark,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }


class EcoArticle(Base):
    """
    环保资讯模型
    """
    __tablename__ = "eco_articles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)  # 标题
    summary = Column(String(500))  # 摘要
    content = Column(Text)  # 内容
    cover_image = Column(String(255))  # 封面图
    category = Column(String(50), default="环保资讯")  # 分类
    author = Column(String(50))  # 作者
    source = Column(String(100))  # 来源
    view_count = Column(Integer, default=0)  # 浏览量
    like_count = Column(Integer, default=0)  # 点赞数
    is_top = Column(Integer, default=0)  # 是否置顶
    is_hot = Column(Integer, default=0)  # 是否热门
    status = Column(Integer, default=1)  # 0: 下架, 1: 发布
    publish_time = Column(DateTime, default=datetime.now)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "cover_image": self.cover_image,
            "category": self.category,
            "author": self.author,
            "source": self.source,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "is_top": self.is_top,
            "is_hot": self.is_hot,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class RecycleProcess(Base):
    """
    回收流程模型
    """
    __tablename__ = "recycle_process"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    step = Column(Integer, nullable=False)  # 步骤序号
    title = Column(String(100), nullable=False)  # 步骤标题
    description = Column(Text)  # 步骤描述
    icon = Column(String(255))  # 图标
    image = Column(String(255))  # 图片
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    
    def to_dict(self):
        return {
            "id": self.id,
            "step": self.step,
            "title": self.title,
            "description": self.description,
            "icon": self.icon,
            "image": self.image,
            "sort_order": self.sort_order,
        }


class ChatSession(Base):
    """
    客服会话模型
    """
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_service_id = Column(Integer)  # 客服ID
    last_message = Column(Text)  # 最后一条消息
    last_message_time = Column(DateTime)  # 最后消息时间
    unread_count = Column(Integer, default=0)  # 未读消息数
    status = Column(Integer, default=1)  # 0: 已结束, 1: 进行中
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "customer_service_id": self.customer_service_id,
            "last_message": self.last_message,
            "last_message_time": self.last_message_time.isoformat() if self.last_message_time else None,
            "unread_count": self.unread_count,
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class ChatMessage(Base):
    """
    客服消息模型
    """
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message_type = Column(String(20), nullable=False)  # 消息类型：text, image, voice, system
    content = Column(Text)  # 消息内容
    media_url = Column(String(255))  # 媒体文件URL
    sender_type = Column(String(20), nullable=False)  # 发送者类型：user, customer_service, system
    sender_id = Column(Integer)  # 发送者ID
    is_read = Column(Integer, default=0)  # 是否已读
    read_time = Column(DateTime)
    create_time = Column(DateTime, default=datetime.now)
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "message_type": self.message_type,
            "content": self.content,
            "media_url": self.media_url,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "is_read": self.is_read,
            "create_time": self.create_time.isoformat() if self.create_time else None,
        }


class Admin(Base):
    """
    管理员模型
    """
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50))
    avatar = Column(String(255))
    role = Column(String(20), default="admin")  # 角色：admin, super_admin, customer_service
    status = Column(Integer, default=1)
    last_login_time = Column(DateTime)
    create_time = Column(DateTime, default=datetime.now)


class SystemConfig(Base):
    """
    系统配置模型
    """
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(Text)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    create_time = Column(DateTime, default=datetime.now)
