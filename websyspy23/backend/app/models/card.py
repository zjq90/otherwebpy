"""
卡项管理数据模型
包含卡类型(CardType)和卡项(Card)两个核心模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class CardType(Base):
    """
    卡类型模型
    定义系统支持的各种卡型：年卡、月卡、次卡、储值卡、私教包等
    """
    
    __tablename__ = "card_types"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="卡类型ID")
    
    # 卡类型名称：年卡、月卡、次卡、储值卡、私教包
    name = Column(String(50), unique=True, nullable=False, index=True, comment="卡类型名称")
    
    # 卡类型代码：yearly, monthly, count, stored, private
    code = Column(String(50), unique=True, nullable=False, index=True, comment="卡类型代码")
    
    # 卡类型描述
    description = Column(Text, comment="卡类型描述")
    
    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：一个卡类型对应多个卡项
    cards = relationship("Card", back_populates="card_type")
    
    def __repr__(self):
        return f"<CardType(id={self.id}, name='{self.name}')>"


class Card(Base):
    """
    卡项模型
    定义具体的卡产品，包含价格、有效期、权益、续费规则等
    """
    
    __tablename__ = "cards"
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="卡项ID")
    
    # 卡项名称
    name = Column(String(100), nullable=False, index=True, comment="卡项名称")
    
    # 外键：关联卡类型
    card_type_id = Column(Integer, ForeignKey("card_types.id"), nullable=False, comment="卡类型ID")
    
    # 价格
    price = Column(Float, nullable=False, comment="价格")
    
    # 原价（用于显示折扣）
    original_price = Column(Float, comment="原价")
    
    # 有效期天数（年卡、月卡使用）
    valid_days = Column(Integer, comment="有效期天数")
    
    # 有效次数（次卡、私教包使用）
    valid_count = Column(Integer, comment="有效次数")
    
    # 储值金额（储值卡使用）
    stored_amount = Column(Float, comment="储值金额")
    
    # 赠送金额（储值卡使用）
    bonus_amount = Column(Float, default=0, comment="赠送金额")
    
    # 包含权益（JSON格式存储，如：{"yoga": true, "spinning": true}）
    benefits = Column(Text, comment="包含权益")
    
    # 续费规则（JSON格式存储，如：{"discount": 0.9, "extend_days": 30}）
    renewal_rules = Column(Text, comment="续费规则")
    
    # 卡项描述
    description = Column(Text, comment="卡项描述")
    
    # 是否启用
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 排序权重
    sort_order = Column(Integer, default=0, comment="排序权重")
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关系：多个卡项对应一个卡类型
    card_type = relationship("CardType", back_populates="cards")
    
    # 关系：一个卡项对应多个会员卡
    member_cards = relationship("MemberCard", back_populates="card")
    
    def __repr__(self):
        return f"<Card(id={self.id}, name='{self.name}', price={self.price})>"
