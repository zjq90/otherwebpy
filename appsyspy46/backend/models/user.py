from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """
    用户表 - 存储回收人员信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(20), unique=True, index=True, comment="手机号")
    avatar = Column(String(255), comment="头像URL")
    id_card = Column(String(20), comment="身份证号")
    
    total_orders = Column(Integer, default=0, comment="总完成订单数")
    total_weight = Column(Float, default=0.0, comment="总回收重量(kg)")
    total_income = Column(Float, default=0.0, comment="总收益(元)")
    
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否实名认证")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    orders = relationship("Order", back_populates="collector")
    withdrawals = relationship("Withdrawal", back_populates="user")


class Withdrawal(Base):
    """
    提现记录表
    """
    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, comment="回收人员ID")
    amount = Column(Float, nullable=False, comment="提现金额(元)")
    bank_card = Column(String(50), comment="银行卡号")
    bank_name = Column(String(50), comment="银行名称")
    account_name = Column(String(50), comment="账户名")
    
    status = Column(String(20), default="pending", comment="状态: pending-待处理, approved-已通过, rejected-已拒绝")
    reject_reason = Column(Text, comment="拒绝原因")
    processed_at = Column(DateTime, comment="处理时间")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    user = relationship("User", back_populates="withdrawals")
