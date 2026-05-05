from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Order(Base):
    """
    订单表模型
    存储回收订单的核心信息
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="订单ID")
    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="订单编号")
    
    # 用户信息
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    user_name = Column(String(50), nullable=True, comment="用户姓名")
    user_phone = Column(String(20), nullable=True, comment="用户电话")
    
    # 回收地址
    address = Column(String(500), nullable=False, comment="回收地址")
    area = Column(String(100), nullable=True, comment="区域")
    
    # 预约信息
    appointment_date = Column(DateTime, nullable=True, comment="预约日期")
    appointment_time = Column(String(50), nullable=True, comment="预约时间段")
    
    # 回收人员信息
    recycler_id = Column(Integer, nullable=True, index=True, comment="回收人员ID")
    recycler_name = Column(String(50), nullable=True, comment="回收人员姓名")
    
    # 订单状态：
    # 0-待接单，1-已接单，2-上门中，3-已完成，4-已取消，5-异常
    status = Column(Integer, default=0, index=True, comment="订单状态")
    
    # 订单金额和重量
    total_weight = Column(Numeric(10, 2), nullable=True, comment="总重量(kg)")
    total_amount = Column(Numeric(10, 2), nullable=True, comment="总金额(元)")
    total_points = Column(Integer, nullable=True, comment="获得积分")
    
    # 备注信息
    remark = Column(Text, nullable=True, comment="备注")
    cancel_reason = Column(String(500), nullable=True, comment="取消原因")
    exception_reason = Column(String(500), nullable=True, comment="异常原因")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    accept_time = Column(DateTime, nullable=True, comment="接单时间")
    complete_time = Column(DateTime, nullable=True, comment="完成时间")
    cancel_time = Column(DateTime, nullable=True, comment="取消时间")

class OrderItem(Base):
    """
    订单明细表模型
    存储订单中具体的衣物明细
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="明细ID")
    order_id = Column(Integer, nullable=False, index=True, comment="订单ID")
    
    # 衣物分类信息
    category_id = Column(Integer, nullable=True, comment="分类ID")
    category_name = Column(String(50), nullable=True, comment="分类名称")
    
    # 计价方式：0-按件，1-按斤
    pricing_type = Column(Integer, default=0, comment="计价方式")
    
    # 数量/重量
    quantity = Column(Integer, nullable=True, comment="数量(件)")
    weight = Column(Numeric(10, 2), nullable=True, comment="重量(kg)")
    
    # 价格信息
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    amount = Column(Numeric(10, 2), nullable=False, comment="小计金额")
    points = Column(Integer, default=0, comment="获得积分")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
