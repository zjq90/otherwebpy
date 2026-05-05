from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.sql import func
from app.database import Base

class ClothingCategory(Base):
    """
    衣物分类表模型
    存储衣物分类信息
    """
    __tablename__ = "clothing_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="分类ID")
    name = Column(String(50), nullable=False, comment="分类名称")
    code = Column(String(20), unique=True, nullable=True, comment="分类编码")
    
    # 父级分类（支持多级分类）
    parent_id = Column(Integer, default=0, index=True, comment="父级分类ID")
    level = Column(Integer, default=1, comment="分类层级")
    sort = Column(Integer, default=0, comment="排序")
    
    # 图标和描述
    icon = Column(String(255), nullable=True, comment="图标")
    description = Column(Text, nullable=True, comment="描述")
    
    # 状态：0-禁用，1-启用
    status = Column(Integer, default=1, index=True, comment="状态")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

class PricingRule(Base):
    """
    计价规则表模型
    存储不同衣物分类的回收价格规则
    支持按件计价和按斤计价两种模式
    """
    __tablename__ = "pricing_rules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="规则ID")
    category_id = Column(Integer, nullable=False, index=True, comment="分类ID")
    category_name = Column(String(50), nullable=True, comment="分类名称")
    
    # 计价方式：0-按件，1-按斤
    pricing_type = Column(Integer, default=1, index=True, comment="计价方式")
    
    # 按件计价
    unit_price = Column(Numeric(10, 2), default=0, comment="单价(元/件)")
    
    # 按斤计价
    weight_price = Column(Numeric(10, 2), default=0, comment="单价(元/公斤)")
    
    # 兜底价格（当按斤价格低于兜底时使用兜底）
    has_min_price = Column(Integer, default=0, comment="是否启用兜底价格")
    min_price_per_item = Column(Numeric(10, 2), default=0, comment="每件兜底价格(元)")
    
    # 积分规则
    points_per_unit = Column(Integer, default=0, comment="每件/每公斤积分")
    
    # 状态：0-禁用，1-启用
    status = Column(Integer, default=1, index=True, comment="状态")
    
    # 生效时间
    effective_date = Column(DateTime, nullable=True, comment="生效日期")
    expiry_date = Column(DateTime, nullable=True, comment="失效日期")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
