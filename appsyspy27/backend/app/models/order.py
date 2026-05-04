"""
订单模型模块
定义订单、支付、消费记录等相关数据库表结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    """
    订单表
    存储购卡、续费、购买商品等订单信息
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 订单号（系统生成的唯一订单号）
    order_no = Column(String(32), unique=True, index=True, nullable=False)
    
    # 关联用户ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 订单类型：PURCHASE(购卡), RENEWAL(续费), GOODS(商品)
    order_type = Column(String(20), nullable=False)
    
    # 关联卡类型ID（购卡/续费时）
    card_type_id = Column(Integer, ForeignKey("card_types.id"), nullable=True)
    
    # 关联商品ID（购买商品时）
    goods_id = Column(Integer, nullable=True)
    
    # 订单标题
    title = Column(String(200), nullable=False)
    
    # 订单描述
    description = Column(Text, nullable=True)
    
    # 商品数量
    quantity = Column(Integer, default=1)
    
    # 商品单价
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    # 订单原价总额
    original_amount = Column(Numeric(10, 2), nullable=False)
    
    # 优惠金额
    discount_amount = Column(Numeric(10, 2), default=0)
    
    # 实付金额
    pay_amount = Column(Numeric(10, 2), nullable=False)
    
    # 支付方式：WECHAT(微信), ALIPAY(支付宝), BALANCE(余额)
    pay_method = Column(String(20), nullable=True)
    
    # 第三方支付订单号
    third_pay_no = Column(String(100), nullable=True)
    
    # 订单状态：PENDING(待支付), PAID(已支付), CANCELLED(已取消), REFUNDED(已退款)
    status = Column(String(20), default="PENDING", nullable=False)
    
    # 支付时间
    pay_time = Column(DateTime, nullable=True)
    
    # 取消时间
    cancel_time = Column(DateTime, nullable=True)
    
    # 关联的优惠活动ID
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)
    
    # 电子合同ID
    contract_id = Column(Integer, nullable=True)
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", backref="orders")
    card_type = relationship("CardType")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_no='{self.order_no}')>"


class ConsumptionRecord(Base):
    """
    消费记录表
    记录所有交易明细：购卡、课程扣费、商品消费等
    """
    __tablename__ = "consumption_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联用户ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 消费类型：
    # PURCHASE(购卡), RENEWAL(续费), LESSON(课程扣费), 
    # GOODS(商品消费), RECHARGE(充值), REFUND(退款)
    record_type = Column(String(20), nullable=False, index=True)
    
    # 关联订单ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # 关联用户卡ID（扣费类消费）
    user_card_id = Column(Integer, ForeignKey("user_cards.id"), nullable=True)
    
    # 消费标题
    title = Column(String(200), nullable=False)
    
    # 消费描述
    description = Column(Text, nullable=True)
    
    # 金额（正数为支出，负数为退款/充值）
    amount = Column(Numeric(10, 2), nullable=False)
    
    # 消费前余额
    balance_before = Column(Numeric(10, 2), nullable=True)
    
    # 消费后余额
    balance_after = Column(Numeric(10, 2), nullable=True)
    
    # 扣次前次数（次卡/课包）
    count_before = Column(Integer, nullable=True)
    
    # 扣次后次数
    count_after = Column(Integer, nullable=True)
    
    # 消耗时长（分钟，时长卡）
    duration_used = Column(Integer, nullable=True)
    
    # 消费门店
    store_name = Column(String(100), nullable=True)
    
    # 操作人（如：教练姓名、收银员姓名）
    operator_name = Column(String(50), nullable=True)
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间（消费时间）
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    # 关系
    user = relationship("User", backref="consumption_records")
    user_card = relationship("UserCard")
    
    def __repr__(self):
        return f"<ConsumptionRecord(id={self.id}, title='{self.title}')>"


class Promotion(Base):
    """
    优惠活动表
    定义阶梯优惠、满减、折扣等促销活动
    """
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 活动名称
    name = Column(String(100), nullable=False)
    
    # 活动编码
    code = Column(String(50), unique=True, index=True, nullable=True)
    
    # 活动类型：DISCOUNT(折扣), FULL_REDUCTION(满减), BUY_GIFT(买赠)
    promotion_type = Column(String(20), nullable=False)
    
    # 活动描述
    description = Column(Text, nullable=True)
    
    # 适用卡类型ID列表（JSON格式）
    applicable_card_types = Column(Text, nullable=True)
    
    # 开始时间
    start_time = Column(DateTime, nullable=True)
    
    # 结束时间
    end_time = Column(DateTime, nullable=True)
    
    # 优惠配置（JSON格式，存储阶梯优惠配置）
    discount_config = Column(Text, nullable=False)
    
    # 排序权重
    sort_order = Column(Integer, default=0)
    
    # 是否启用
    is_active = Column(Boolean, default=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Promotion(id={self.id}, name='{self.name}')>"
