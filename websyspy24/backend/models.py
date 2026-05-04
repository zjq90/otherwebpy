"""
数据模型定义模块
定义所有数据库表的结构和关系
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base


class Member(Base):
    """
    会员表模型
    存储会员的基本信息和会籍状态
    """
    __tablename__ = "members"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 会员编号（唯一）
    member_no = Column(String(50), unique=True, index=True, nullable=False)
    # 会员姓名
    name = Column(String(100), nullable=False)
    # 身份证号
    id_card = Column(String(18), nullable=True)
    # 手机号码
    phone = Column(String(20), nullable=True)
    # 邮箱地址
    email = Column(String(100), nullable=True)
    # 卡号（用于刷卡签到）
    card_no = Column(String(50), unique=True, index=True, nullable=True)
    # 二维码内容（用于扫码签到）
    qr_code = Column(String(255), unique=True, index=True, nullable=True)
    # 人脸特征数据（用于人脸识别签到）
    face_data = Column(Text, nullable=True)
    # 会籍类型（如月卡、季卡、年卡）
    membership_type = Column(String(50), nullable=False, default="月卡")
    # 会籍开始日期
    membership_start = Column(Date, nullable=False, default=date.today)
    # 会籍到期日期
    membership_end = Column(Date, nullable=False)
    # 账户余额（用于消费）
    balance = Column(Float, nullable=False, default=0.0)
    # 会员状态（active: 激活, expired: 过期, suspended: 暂停）
    status = Column(String(20), nullable=False, default="active")
    # 备注信息
    remarks = Column(Text, nullable=True)
    # 创建时间
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义：一个会员可以有多个签到记录
    check_ins = relationship("CheckIn", back_populates="member")
    # 关系定义：一个会员可以有多个储物柜使用记录
    locker_usages = relationship("LockerUsage", back_populates="member")
    # 关系定义：一个会员可以有多个订单
    orders = relationship("Order", back_populates="member")


class CheckIn(Base):
    """
    签到记录表模型
    记录会员的签到信息，包括签到方式和验证结果
    """
    __tablename__ = "check_ins"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    # 签到方式（card: 刷卡, qr: 扫码, face: 人脸识别）
    check_in_type = Column(String(20), nullable=False)
    # 签到时间
    check_in_time = Column(DateTime, nullable=False, default=datetime.now)
    # 签到状态（success: 成功, failed: 失败）
    status = Column(String(20), nullable=False, default="success")
    # 失败原因（当status为failed时记录）
    fail_reason = Column(String(255), nullable=True)
    # 验证详情（如人脸相似度、卡号等）
    verification_details = Column(Text, nullable=True)
    # 签到设备编号
    device_no = Column(String(50), nullable=True)
    # 备注信息
    remarks = Column(Text, nullable=True)
    
    # 关系定义：签到记录属于一个会员
    member = relationship("Member", back_populates="check_ins")


class Locker(Base):
    """
    储物柜表模型
    管理储物柜的编号、状态和位置信息
    """
    __tablename__ = "lockers"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 储物柜编号（如A001、B023）
    locker_no = Column(String(20), unique=True, index=True, nullable=False)
    # 储物柜位置描述
    location = Column(String(100), nullable=True)
    # 储物柜类型（small: 小型, medium: 中型, large: 大型）
    locker_type = Column(String(20), nullable=False, default="medium")
    # 储物柜状态（available: 空闲, occupied: 占用, maintenance: 故障维修）
    status = Column(String(20), nullable=False, default="available")
    # 最后状态更新时间
    status_updated_at = Column(DateTime, nullable=False, default=datetime.now)
    # 备注信息
    remarks = Column(Text, nullable=True)
    
    # 关系定义：一个储物柜可以有多个使用记录
    usages = relationship("LockerUsage", back_populates="locker")


class LockerUsage(Base):
    """
    储物柜使用记录表模型
    记录储物柜的分配、使用和归还情况
    """
    __tablename__ = "locker_usages"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    # 关联的储物柜ID
    locker_id = Column(Integer, ForeignKey("lockers.id"), nullable=False)
    # 分配方式（auto: 自动分配, manual: 手动选择）
    assign_type = Column(String(20), nullable=False, default="auto")
    # 开始使用时间
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    # 结束使用时间
    end_time = Column(DateTime, nullable=True)
    # 使用状态（active: 使用中, returned: 已归还, overdue: 逾期）
    status = Column(String(20), nullable=False, default="active")
    # 密码（如果是密码锁）
    password = Column(String(20), nullable=True)
    # 备注信息
    remarks = Column(Text, nullable=True)
    
    # 关系定义：使用记录属于一个会员
    member = relationship("Member", back_populates="locker_usages")
    # 关系定义：使用记录属于一个储物柜
    locker = relationship("Locker", back_populates="usages")


class Product(Base):
    """
    商品表模型
    存储可售卖商品的信息，用于收银功能
    """
    __tablename__ = "products"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 商品编码
    product_code = Column(String(50), unique=True, index=True, nullable=False)
    # 商品名称
    name = Column(String(100), nullable=False)
    # 商品分类（如饮料、食品、周边等）
    category = Column(String(50), nullable=True)
    # 销售价格
    price = Column(Float, nullable=False, default=0.0)
    # 成本价格
    cost_price = Column(Float, nullable=True, default=0.0)
    # 库存数量
    stock_quantity = Column(Integer, nullable=False, default=0)
    # 库存预警数量
    warning_quantity = Column(Integer, nullable=False, default=10)
    # 商品状态（active: 在售, inactive: 下架）
    status = Column(String(20), nullable=False, default="active")
    # 商品描述
    description = Column(Text, nullable=True)
    # 创建时间
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    # 更新时间
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # 关系定义：一个商品可以出现在多个订单明细中
    order_items = relationship("OrderItem", back_populates="product")


class Coupon(Base):
    """
    优惠券表模型
    管理优惠券的信息和使用状态
    """
    __tablename__ = "coupons"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 优惠券码
    coupon_code = Column(String(50), unique=True, index=True, nullable=False)
    # 优惠券名称
    name = Column(String(100), nullable=False)
    # 优惠券类型（discount: 折扣券, cash: 代金券, gift: 赠品券）
    coupon_type = Column(String(20), nullable=False, default="discount")
    # 折扣值（如0.8表示8折，100表示抵扣100元）
    value = Column(Float, nullable=False, default=0.0)
    # 最低消费金额限制
    min_amount = Column(Float, nullable=False, default=0.0)
    # 发放时间
    issue_time = Column(DateTime, nullable=False, default=datetime.now)
    # 过期时间
    expire_time = Column(DateTime, nullable=False)
    # 优惠券状态（available: 可用, used: 已使用, expired: 已过期）
    status = Column(String(20), nullable=False, default="available")
    # 使用时间
    used_time = Column(DateTime, nullable=True)
    # 使用订单ID
    used_order_id = Column(Integer, nullable=True)
    # 关联会员ID（可为空，表示通用券）
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    # 备注信息
    remarks = Column(Text, nullable=True)


class Order(Base):
    """
    订单表模型
    记录消费订单的基本信息
    """
    __tablename__ = "orders"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 订单编号（唯一）
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    # 关联的会员ID（可为空，表示散客）
    member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    # 订单类型（product: 商品购买, recharge: 会员充值, membership: 会籍购买）
    order_type = Column(String(20), nullable=False, default="product")
    # 订单总金额
    total_amount = Column(Float, nullable=False, default=0.0)
    # 优惠金额
    discount_amount = Column(Float, nullable=False, default=0.0)
    # 实际支付金额
    actual_amount = Column(Float, nullable=False, default=0.0)
    # 支付方式（cash: 现金, wechat: 微信, alipay: 支付宝, card: 会员卡）
    payment_method = Column(String(20), nullable=True)
    # 使用的优惠券码
    coupon_code = Column(String(50), nullable=True)
    # 订单状态（pending: 待支付, paid: 已支付, cancelled: 已取消, refunded: 已退款）
    status = Column(String(20), nullable=False, default="pending")
    # 下单时间
    order_time = Column(DateTime, nullable=False, default=datetime.now)
    # 支付时间
    pay_time = Column(DateTime, nullable=True)
    # 收银员ID或名称
    cashier = Column(String(50), nullable=True)
    # 备注信息
    remarks = Column(Text, nullable=True)
    
    # 关系定义：订单属于一个会员
    member = relationship("Member", back_populates="orders")
    # 关系定义：一个订单包含多个订单明细
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    订单明细表模型
    记录订单中的商品明细
    """
    __tablename__ = "order_items"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 关联的订单ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    # 关联的商品ID
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    # 商品名称（冗余存储，方便查看）
    product_name = Column(String(100), nullable=False)
    # 商品单价
    unit_price = Column(Float, nullable=False, default=0.0)
    # 购买数量
    quantity = Column(Integer, nullable=False, default=1)
    # 明细小计金额
    subtotal = Column(Float, nullable=False, default=0.0)
    # 备注信息
    remarks = Column(Text, nullable=True)
    
    # 关系定义：订单明细属于一个订单
    order = relationship("Order", back_populates="order_items")
    # 关系定义：订单明细属于一个商品
    product = relationship("Product", back_populates="order_items")


class PaymentRecord(Base):
    """
    支付记录表模型
    记录每一笔支付的详细信息，用于对账
    """
    __tablename__ = "payment_records"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 关联的订单ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    # 订单编号
    order_no = Column(String(50), nullable=False)
    # 支付流水号（第三方支付平台返回）
    transaction_no = Column(String(100), nullable=True)
    # 支付方式
    payment_method = Column(String(20), nullable=False)
    # 支付金额
    amount = Column(Float, nullable=False, default=0.0)
    # 支付状态（success: 成功, failed: 失败, pending: 处理中）
    status = Column(String(20), nullable=False, default="pending")
    # 支付时间
    pay_time = Column(DateTime, nullable=True)
    # 支付平台返回的原始数据
    raw_data = Column(Text, nullable=True)
    # 对账状态（unreconciled: 未对账, reconciled: 已对账, exception: 异常）
    reconcile_status = Column(String(20), nullable=False, default="unreconciled")
    # 对账时间
    reconcile_time = Column(DateTime, nullable=True)
    # 备注信息
    remarks = Column(Text, nullable=True)


class RechargeRecord(Base):
    """
    会员充值记录表模型
    记录会员的充值信息
    """
    __tablename__ = "recharge_records"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 关联的会员ID
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    # 关联的订单ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    # 充值金额
    recharge_amount = Column(Float, nullable=False, default=0.0)
    # 赠送金额
    gift_amount = Column(Float, nullable=False, default=0.0)
    # 支付方式
    payment_method = Column(String(20), nullable=False)
    # 充值前余额
    balance_before = Column(Float, nullable=False, default=0.0)
    # 充值后余额
    balance_after = Column(Float, nullable=False, default=0.0)
    # 充值状态（success: 成功, failed: 失败）
    status = Column(String(20), nullable=False, default="success")
    # 充值时间
    recharge_time = Column(DateTime, nullable=False, default=datetime.now)
    # 操作人
    operator = Column(String(50), nullable=True)
    # 备注信息
    remarks = Column(Text, nullable=True)
