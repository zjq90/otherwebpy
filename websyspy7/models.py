"""
数据库模型定义
包含所有数据表的ORM映射
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    系统用户表
    用于登录本系统的用户信息
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    email = Column(String(100), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    passengers = relationship("Passenger", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    monitor_tasks = relationship("MonitorTask", back_populates="user")
    orders = relationship("Order", back_populates="user")
    alerts = relationship("AlertRecord", back_populates="user")


class Passenger(Base):
    """
    抢单人信息表
    登记抢单人的姓名、身份证号等信息
    """
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True, comment="抢单人ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="所属系统用户ID")
    name = Column(String(50), nullable=False, comment="姓名")
    id_card = Column(String(18), nullable=False, comment="身份证号")
    phone = Column(String(20), nullable=True, comment="手机号")
    passenger_type = Column(String(20), default="成人", comment="乘客类型：成人/儿童/学生/残疾军人")
    is_default = Column(Boolean, default=False, comment="是否默认抢单人")
    status = Column(String(20), default="active", comment="状态：active/inactive")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="passengers")


class UserSession(Base):
    """
    用户会话凭证表
    存储从票务系统获取的Session ID、Cookie、Access Token等
    """
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True, comment="会话ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="所属系统用户ID")
    session_id = Column(String(255), nullable=True, comment="Session ID")
    cookie = Column(Text, nullable=True, comment="Cookie字符串")
    access_token = Column(Text, nullable=True, comment="Access Token")
    refresh_token = Column(Text, nullable=True, comment="Refresh Token")
    ticket_username = Column(String(100), nullable=True, comment="票务系统用户名")
    expires_at = Column(DateTime, nullable=True, comment="过期时间")
    user_agent = Column(String(500), nullable=True, comment="User-Agent")
    referer = Column(String(500), nullable=True, comment="Referer")
    is_valid = Column(Boolean, default=True, comment="是否有效")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="sessions")


class MonitorTask(Base):
    """
    监控任务表
    存储用户的余票监控条件配置
    """
    __tablename__ = "monitor_tasks"
    
    id = Column(Integer, primary_key=True, index=True, comment="任务ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="所属系统用户ID")
    task_name = Column(String(100), nullable=False, comment="任务名称")
    
    # 监控条件
    from_station = Column(String(50), nullable=False, comment="出发站")
    to_station = Column(String(50), nullable=False, comment="到达站")
    train_date = Column(String(20), nullable=False, comment="出发日期（格式：YYYY-MM-DD）")
    train_numbers = Column(Text, nullable=True, comment="指定车次（逗号分隔，为空则监控所有）")
    
    # 席别/票价区间
    seat_types = Column(Text, nullable=True, comment="席别（逗号分隔：商务座/一等座/二等座/软卧/硬卧/硬座）")
    min_price = Column(Float, nullable=True, comment="最低票价")
    max_price = Column(Float, nullable=True, comment="最高票价")
    
    # 乘客配置
    passenger_ids = Column(Text, nullable=True, comment="抢单人ID列表（逗号分隔）")
    
    # 监控配置
    poll_interval = Column(Float, default=1.0, comment="轮询间隔（秒）")
    auto_submit = Column(Boolean, default=False, comment="是否自动提交订单")
    max_retries = Column(Integer, default=3, comment="最大重试次数")
    
    # 状态
    status = Column(String(20), default="stopped", comment="状态：running/stopped/completed/failed")
    last_check_time = Column(DateTime, nullable=True, comment="上次检查时间")
    last_check_result = Column(Text, nullable=True, comment="上次检查结果")
    ticket_found = Column(Boolean, default=False, comment="是否发现有余票")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="monitor_tasks")
    orders = relationship("Order", back_populates="monitor_task")


class Order(Base):
    """
    订单表
    存储自动提交的订单信息
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, comment="订单ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="所属系统用户ID")
    monitor_task_id = Column(Integer, ForeignKey("monitor_tasks.id"), nullable=True, comment="关联的监控任务ID")
    
    # 订单信息
    order_no = Column(String(50), unique=True, index=True, nullable=True, comment="订单号")
    train_number = Column(String(20), nullable=False, comment="车次")
    from_station = Column(String(50), nullable=False, comment="出发站")
    to_station = Column(String(50), nullable=False, comment="到达站")
    depart_time = Column(String(20), nullable=True, comment="出发时间")
    arrive_time = Column(String(20), nullable=True, comment="到达时间")
    train_date = Column(String(20), nullable=False, comment="乘车日期")
    
    # 乘客与座位
    passenger_info = Column(Text, nullable=False, comment="乘客信息（JSON格式）")
    seat_type = Column(String(20), nullable=False, comment="席别")
    seat_no = Column(String(50), nullable=True, comment="座位号")
    ticket_price = Column(Float, nullable=False, comment="票价")
    total_amount = Column(Float, nullable=False, comment="总金额")
    
    # 订单状态
    status = Column(String(20), default="pending", comment="订单状态：pending/submitted/paid/cancelled/failed")
    submit_time = Column(DateTime, nullable=True, comment="提交时间")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    cancel_time = Column(DateTime, nullable=True, comment="取消时间")
    pay_deadline = Column(DateTime, nullable=True, comment="支付截止时间")
    
    # 其他
    external_order_id = Column(String(100), nullable=True, comment="外部系统订单ID")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="orders")
    monitor_task = relationship("MonitorTask", back_populates="orders")


class AlertRecord(Base):
    """
    提醒记录表
    存储系统发出的提醒记录
    """
    __tablename__ = "alert_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="提醒ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="所属系统用户ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, comment="关联订单ID")
    monitor_task_id = Column(Integer, ForeignKey("monitor_tasks.id"), nullable=True, comment="关联监控任务ID")
    
    alert_type = Column(String(20), nullable=False, comment="提醒类型：sms/email/system")
    alert_title = Column(String(200), nullable=False, comment="提醒标题")
    alert_content = Column(Text, nullable=False, comment="提醒内容")
    
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_time = Column(DateTime, nullable=True, comment="阅读时间")
    
    is_sent = Column(Boolean, default=False, comment="是否已发送")
    sent_time = Column(DateTime, nullable=True, comment="发送时间")
    send_error = Column(Text, nullable=True, comment="发送错误信息")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="alerts")


class Station(Base):
    """
    站点信息表（用于测试和缓存）
    """
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True, comment="站点ID")
    station_name = Column(String(50), nullable=False, comment="站点名称")
    station_code = Column(String(10), unique=True, index=True, nullable=False, comment="站点电报码")
    station_pinyin = Column(String(100), nullable=True, comment="站点拼音")
    province = Column(String(50), nullable=True, comment="省份")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")


class TrainInfo(Base):
    """
    车次信息表（用于测试和缓存）
    """
    __tablename__ = "train_infos"
    
    id = Column(Integer, primary_key=True, index=True, comment="ID")
    train_number = Column(String(20), unique=True, index=True, nullable=False, comment="车次号")
    train_type = Column(String(20), nullable=False, comment="列车类型：G/D/C/Z/T/K等")
    from_station = Column(String(50), nullable=False, comment="始发站")
    to_station = Column(String(50), nullable=False, comment="终点站")
    depart_time = Column(String(20), nullable=True, comment="发车时间")
    arrive_time = Column(String(20), nullable=True, comment="到达时间")
    duration = Column(String(20), nullable=True, comment="运行时长")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
