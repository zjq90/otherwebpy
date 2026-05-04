"""
会员卡模型模块
定义会员卡类型、用户卡包等相关数据库表结构
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CardType(Base):
    """
    会员卡类型表
    定义系统支持的所有会员卡类型（年卡、次卡、私教课包等）
    """
    __tablename__ = "card_types"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 卡类型名称（如：年度会员、20次次卡、私教10节套餐）
    name = Column(String(100), nullable=False)
    
    # 卡类型编码（如：YEAR_CARD, COUNT_CARD, PRIVATE_LESSON）
    code = Column(String(50), unique=True, index=True, nullable=False)
    
    # 卡类型描述
    description = Column(Text, nullable=True)
    
    # 卡类型分类：YEAR(年卡), COUNT(次卡), DURATION(时长卡), LESSON(课包)
    category = Column(String(20), nullable=False)
    
    # 原价
    original_price = Column(Numeric(10, 2), nullable=False)
    
    # 当前售价
    current_price = Column(Numeric(10, 2), nullable=False)
    
    # 有效期天数（如：年卡365天），为None表示永久有效
    valid_days = Column(Integer, nullable=True)
    
    # 总次数（次卡/课包专用）
    total_count = Column(Integer, nullable=True)
    
    # 总时长（分钟，时长卡专用）
    total_duration = Column(Integer, nullable=True)
    
    # 使用范围描述
    usage_scope = Column(Text, nullable=True)
    
    # 适用门店ID列表（JSON格式）
    applicable_stores = Column(Text, nullable=True)
    
    # 是否上架销售
    is_on_sale = Column(Boolean, default=True)
    
    # 排序权重（越大越靠前）
    sort_order = Column(Integer, default=0)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<CardType(id={self.id}, name='{self.name}')>"


class UserCard(Base):
    """
    用户会员卡包表
    存储用户持有的所有会员卡实例
    """
    __tablename__ = "user_cards"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联用户ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 关联卡类型ID
    card_type_id = Column(Integer, ForeignKey("card_types.id"), nullable=False)
    
    # 卡号（系统生成的唯一卡号）
    card_number = Column(String(32), unique=True, index=True, nullable=False)
    
    # 卡的显示名称（可以覆盖卡类型名称）
    display_name = Column(String(100), nullable=True)
    
    # 购买时间
    purchase_time = Column(DateTime, default=datetime.now)
    
    # 激活时间
    activate_time = Column(DateTime, nullable=True)
    
    # 过期时间
    expire_time = Column(Date, nullable=True)
    
    # 剩余次数（次卡/课包）
    remaining_count = Column(Integer, nullable=True)
    
    # 总次数（购买时的次数）
    total_count = Column(Integer, nullable=True)
    
    # 剩余时长（分钟，时长卡）
    remaining_duration = Column(Integer, nullable=True)
    
    # 总时长
    total_duration = Column(Integer, nullable=True)
    
    # 卡状态：ACTIVE(有效), EXPIRED(已过期), USED_UP(已用完), FROZEN(已冻结)
    status = Column(String(20), default="ACTIVE", nullable=False)
    
    # 购买订单ID
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    # 备注
    remark = Column(Text, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", backref="user_cards")
    card_type = relationship("CardType")
    
    def is_valid(self):
        """检查卡是否有效（未过期、未用完、未冻结）"""
        if self.status != "ACTIVE":
            return False
        if self.expire_time and date.today() > self.expire_time:
            return False
        if self.remaining_count is not None and self.remaining_count <= 0:
            return False
        if self.remaining_duration is not None and self.remaining_duration <= 0:
            return False
        return True
    
    def __repr__(self):
        return f"<UserCard(id={self.id}, card_number='{self.card_number}')>"
