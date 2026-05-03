"""
数据库模型定义
包含所有数据表的ORM模型定义
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    用户模型
    存储系统所有用户信息，包括管理员、工作人员和租借人员
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密存储）")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    email = Column(String(100), comment="邮箱")
    role = Column(String(20), nullable=False, default="renter", 
                  comment="角色：admin-管理员, staff-工作人员, renter-租借人员")
    balance = Column(Float, default=0.0, comment="账户余额")
    status = Column(String(20), default="active", comment="状态：active-激活, inactive-禁用")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    rentals = relationship("Rental", back_populates="renter")
    reminders = relationship("Reminder", back_populates="user")


class Item(Base):
    """
    物品模型
    存储可租借物品的信息
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="物品名称")
    description = Column(Text, comment="物品描述")
    category = Column(String(50), comment="物品分类")
    daily_rent = Column(Float, nullable=False, comment="日租金")
    deposit = Column(Float, nullable=False, comment="押金")
    stock = Column(Integer, default=1, comment="库存数量")
    available = Column(Integer, default=1, comment="可用数量")
    status = Column(String(20), default="available", 
                    comment="状态：available-可用, unavailable-不可用, maintenance-维护中")
    image_url = Column(String(255), comment="物品图片URL")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    rentals = relationship("Rental", back_populates="item")


class Rental(Base):
    """
    租借记录模型
    存储物品租借的交易记录
    """
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    rental_no = Column(String(50), unique=True, index=True, nullable=False, comment="租借单号")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="租借人ID")
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, comment="物品ID")
    quantity = Column(Integer, default=1, comment="租借数量")
    start_date = Column(Date, nullable=False, comment="租借开始日期")
    due_date = Column(Date, nullable=False, comment="应归还日期")
    actual_return_date = Column(Date, comment="实际归还日期")
    daily_rent = Column(Float, nullable=False, comment="租借时的日租金")
    deposit_amount = Column(Float, nullable=False, comment="押金金额")
    total_rent = Column(Float, default=0.0, comment="总租金")
    deposit_status = Column(String(20), default="paid", 
                             comment="押金状态：paid-已缴纳, refunded-已退还, deducted-已扣除")
    status = Column(String(20), default="active", 
                    comment="状态：active-租借中, returned-已归还, overdue-逾期, completed-已完成")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    renter = relationship("User", back_populates="rentals")
    item = relationship("Item", back_populates="rentals")
    reminders = relationship("Reminder", back_populates="rental")
    collection_orders = relationship("CollectionOrder", back_populates="rental")


class Reminder(Base):
    """
    提醒记录模型
    存储所有提醒的历史记录，包括平台提醒和短信提醒
    """
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False, comment="关联的租借记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收提醒的用户ID")
    reminder_type = Column(String(20), nullable=False, 
                            comment="提醒类型：platform-平台提醒, sms-短信提醒")
    reminder_level = Column(String(20), default="normal", 
                            comment="提醒级别：normal-正常, urgent-紧急, critical-严重")
    title = Column(String(200), nullable=False, comment="提醒标题")
    content = Column(Text, nullable=False, comment="提醒内容")
    is_read = Column(Boolean, default=False, comment="是否已读（平台提醒专用）")
    is_sent = Column(Boolean, default=False, comment="是否已发送（短信提醒专用）")
    sent_at = Column(DateTime, comment="发送时间")
    reminder_day = Column(Integer, comment="第几次提醒（1-3）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    rental = relationship("Rental", back_populates="reminders")
    user = relationship("User", back_populates="reminders")


class CollectionOrder(Base):
    """
    催还订单模型
    系统自动生成的催还订单，用于平台提醒
    """
    __tablename__ = "collection_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False, comment="催还单号")
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False, comment="关联的租借记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="租借人ID")
    overdue_days = Column(Integer, default=0, comment="逾期天数")
    total_amount = Column(Float, default=0.0, comment="应缴金额（租金+可能的罚款）")
    status = Column(String(20), default="pending", 
                    comment="状态：pending-待处理, processing-处理中, resolved-已解决, deducted-已扣押金")
    is_urgent = Column(Boolean, default=False, comment="是否紧急")
    handled_by = Column(Integer, ForeignKey("users.id"), comment="处理人ID（工作人员）")
    handled_at = Column(DateTime, comment="处理时间")
    remark = Column(Text, comment="处理备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    rental = relationship("Rental", back_populates="collection_orders")


class SMSLog(Base):
    """
    短信发送日志模型
    记录所有短信发送的详细信息
    """
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False, comment="接收手机号")
    template_code = Column(String(50), comment="短信模板代码")
    template_param = Column(Text, comment="模板参数（JSON格式）")
    content = Column(Text, comment="短信内容")
    status = Column(String(20), default="pending", 
                    comment="状态：pending-待发送, success-发送成功, failed-发送失败")
    provider_response = Column(Text, comment="短信服务商响应")
    reminder_id = Column(Integer, ForeignKey("reminders.id"), comment="关联的提醒记录ID")
    sent_at = Column(DateTime, comment="发送时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class SystemConfig(Base):
    """
    系统配置模型
    存储系统运行时的配置参数
    """
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False, comment="配置键")
    config_value = Column(Text, comment="配置值")
    description = Column(String(255), comment="配置描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
