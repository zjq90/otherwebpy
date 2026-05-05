from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Order(Base):
    """
    订单表 - 存储回收订单信息
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(32), unique=True, index=True, nullable=False, comment="订单编号")
    
    user_name = Column(String(50), comment="用户姓名")
    user_phone = Column(String(20), comment="用户电话")
    address = Column(String(255), nullable=False, comment="详细地址")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    latitude = Column(Float, comment="纬度")
    longitude = Column(Float, comment="经度")
    
    clothing_types = Column(String(255), comment="衣物类型(多个用逗号分隔)")
    estimated_weight = Column(Float, comment="预估重量(kg)")
    estimated_quantity = Column(Integer, comment="预估数量(件)")
    description = Column(Text, comment="补充说明")
    
    collector_id = Column(Integer, ForeignKey("users.id"), comment="回收人员ID")
    
    actual_weight = Column(Float, comment="实际重量(kg)")
    actual_quantity = Column(Integer, comment="实际数量(件)")
    recycle_photos = Column(Text, comment="回收照片URL(多个用逗号分隔)")
    unit_price = Column(Float, default=2.0, comment="单价(元/kg)")
    total_amount = Column(Float, comment="总金额(元)")
    
    status = Column(String(20), default="pending", comment="订单状态: pending-待接单, accepted-已接单, rejected-已拒绝, processing-回收中, completed-已完成, cancelled-已取消")
    reject_reason = Column(Text, comment="拒绝原因")
    cancel_reason = Column(Text, comment="取消原因")
    
    appointment_time = Column(DateTime, comment="预约时间")
    accepted_at = Column(DateTime, comment="接单时间")
    completed_at = Column(DateTime, comment="完成时间")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    collector = relationship("User", back_populates="orders")
    logs = relationship("OrderLog", back_populates="order")


class OrderLog(Base):
    """
    订单操作日志表
    """
    __tablename__ = "order_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), comment="订单ID")
    operator_type = Column(String(20), comment="操作人类型: user-用户, collector-回收员, system-系统")
    operator_id = Column(Integer, comment="操作人ID")
    action = Column(String(50), comment="操作动作")
    description = Column(Text, comment="操作描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    order = relationship("Order", back_populates="logs")
