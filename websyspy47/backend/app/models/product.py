from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    """
    积分商品表模型
    存储积分兑换的商品信息
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="商品ID")
    product_name = Column(String(200), nullable=False, comment="商品名称")
    product_code = Column(String(50), unique=True, nullable=True, comment="商品编码")
    
    # 商品分类
    category_id = Column(Integer, nullable=True, index=True, comment="分类ID")
    category_name = Column(String(50), nullable=True, comment="分类名称")
    
    # 价格设置
    points_price = Column(Integer, nullable=False, comment="积分价格")
    original_price = Column(Numeric(10, 2), nullable=True, comment="原价(元)")
    
    # 库存管理
    stock = Column(Integer, default=0, comment="库存数量")
    sold_count = Column(Integer, default=0, comment="已兑换数量")
    min_limit = Column(Integer, default=1, comment="最低兑换数量")
    max_limit = Column(Integer, default=10, comment="每人最多兑换数量")
    
    # 商品信息
    image = Column(String(500), nullable=True, comment="商品图片")
    description = Column(Text, nullable=True, comment="商品描述")
    specification = Column(String(500), nullable=True, comment="规格")
    
    # 状态：0-下架，1-上架
    status = Column(Integer, default=0, index=True, comment="状态")
    sort = Column(Integer, default=0, comment="排序")
    
    # 兑换规则
    exchange_start_time = Column(DateTime, nullable=True, comment="兑换开始时间")
    exchange_end_time = Column(DateTime, nullable=True, comment="兑换结束时间")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

class PointsRule(Base):
    """
    积分规则表模型
    存储不同类型衣物对应的积分奖励标准
    """
    __tablename__ = "points_rules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="规则ID")
    name = Column(String(100), nullable=False, comment="规则名称")
    
    # 关联分类
    category_id = Column(Integer, nullable=True, index=True, comment="分类ID")
    category_name = Column(String(50), nullable=True, comment="分类名称")
    
    # 积分设置
    # 计价方式：0-按件，1-按斤
    pricing_type = Column(Integer, default=1, comment="计价方式")
    points_per_unit = Column(Integer, default=0, comment="每件/每公斤积分")
    
    # 额外奖励
    has_bonus = Column(Integer, default=0, comment="是否有额外奖励")
    bonus_condition = Column(String(200), nullable=True, comment="奖励条件")
    bonus_points = Column(Integer, default=0, comment="奖励积分")
    
    # 状态：0-禁用，1-启用
    status = Column(Integer, default=1, index=True, comment="状态")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

class PointsExchange(Base):
    """
    积分兑换记录表模型
    存储用户积分兑换商品的记录
    """
    __tablename__ = "points_exchanges"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="记录ID")
    exchange_no = Column(String(50), unique=True, nullable=False, comment="兑换单号")
    
    # 用户信息
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    user_name = Column(String(50), nullable=True, comment="用户姓名")
    user_phone = Column(String(20), nullable=True, comment="用户电话")
    
    # 商品信息
    product_id = Column(Integer, nullable=False, comment="商品ID")
    product_name = Column(String(200), nullable=False, comment="商品名称")
    product_image = Column(String(500), nullable=True, comment="商品图片")
    
    # 兑换信息
    quantity = Column(Integer, default=1, comment="兑换数量")
    points_price = Column(Integer, nullable=False, comment="商品积分单价")
    total_points = Column(Integer, nullable=False, comment="消耗积分总数")
    
    # 收货信息
    receive_name = Column(String(50), nullable=True, comment="收货人姓名")
    receive_phone = Column(String(20), nullable=True, comment="收货人电话")
    receive_address = Column(String(500), nullable=True, comment="收货地址")
    
    # 状态：0-待发货，1-已发货，2-已收货，3-已取消
    status = Column(Integer, default=0, index=True, comment="状态")
    logistics_company = Column(String(100), nullable=True, comment="物流公司")
    logistics_no = Column(String(100), nullable=True, comment="物流单号")
    
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
