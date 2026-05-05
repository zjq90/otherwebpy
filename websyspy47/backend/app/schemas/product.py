from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    """商品基础模型"""
    product_name: str = Field(..., max_length=200, description="商品名称")
    product_code: Optional[str] = Field(None, max_length=50, description="商品编码")
    category_id: Optional[int] = None
    category_name: Optional[str] = Field(None, max_length=50, description="分类名称")
    points_price: int = Field(..., description="积分价格")
    original_price: Optional[Decimal] = None
    stock: int = Field(0, description="库存数量")
    sold_count: int = Field(0, description="已兑换数量")
    min_limit: int = Field(1, description="最低兑换数量")
    max_limit: int = Field(10, description="每人最多兑换数量")
    image: Optional[str] = Field(None, max_length=500, description="商品图片")
    description: Optional[str] = None
    specification: Optional[str] = Field(None, max_length=500, description="规格")
    status: Optional[int] = Field(0, description="状态：0-下架，1-上架")
    sort: int = Field(0, description="排序")
    exchange_start_time: Optional[datetime] = None
    exchange_end_time: Optional[datetime] = None

class ProductCreate(ProductBase):
    """商品创建模型"""
    pass

class ProductUpdate(BaseModel):
    """商品更新模型"""
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    points_price: Optional[int] = None
    original_price: Optional[Decimal] = None
    stock: Optional[int] = None
    sold_count: Optional[int] = None
    min_limit: Optional[int] = None
    max_limit: Optional[int] = None
    image: Optional[str] = None
    description: Optional[str] = None
    specification: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None
    exchange_start_time: Optional[datetime] = None
    exchange_end_time: Optional[datetime] = None

class ProductResponse(ProductBase):
    """商品响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PointsRuleBase(BaseModel):
    """积分规则基础模型"""
    name: str = Field(..., max_length=100, description="规则名称")
    category_id: Optional[int] = None
    category_name: Optional[str] = Field(None, max_length=50, description="分类名称")
    pricing_type: int = Field(1, description="计价方式：0-按件，1-按斤")
    points_per_unit: int = Field(0, description="每件/每公斤积分")
    has_bonus: int = Field(0, description="是否有额外奖励")
    bonus_condition: Optional[str] = Field(None, max_length=200, description="奖励条件")
    bonus_points: int = Field(0, description="奖励积分")
    status: Optional[int] = Field(1, description="状态：0-禁用，1-启用")

class PointsRuleCreate(PointsRuleBase):
    """积分规则创建模型"""
    pass

class PointsRuleUpdate(BaseModel):
    """积分规则更新模型"""
    name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    pricing_type: Optional[int] = None
    points_per_unit: Optional[int] = None
    has_bonus: Optional[int] = None
    bonus_condition: Optional[str] = None
    bonus_points: Optional[int] = None
    status: Optional[int] = None

class PointsRuleResponse(PointsRuleBase):
    """积分规则响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PointsExchangeBase(BaseModel):
    """积分兑换记录基础模型"""
    exchange_no: str = Field(..., max_length=50, description="兑换单号")
    user_id: int
    user_name: Optional[str] = Field(None, max_length=50, description="用户姓名")
    user_phone: Optional[str] = Field(None, max_length=20, description="用户电话")
    product_id: int
    product_name: str = Field(..., max_length=200, description="商品名称")
    product_image: Optional[str] = Field(None, max_length=500, description="商品图片")
    quantity: int = Field(1, description="兑换数量")
    points_price: int = Field(..., description="商品积分单价")
    total_points: int = Field(..., description="消耗积分总数")
    receive_name: Optional[str] = Field(None, max_length=50, description="收货人姓名")
    receive_phone: Optional[str] = Field(None, max_length=20, description="收货人电话")
    receive_address: Optional[str] = Field(None, max_length=500, description="收货地址")
    status: Optional[int] = Field(0, description="状态")
    logistics_company: Optional[str] = Field(None, max_length=100, description="物流公司")
    logistics_no: Optional[str] = Field(None, max_length=100, description="物流单号")

class PointsExchangeCreate(PointsExchangeBase):
    """积分兑换记录创建模型"""
    pass

class PointsExchangeUpdate(BaseModel):
    """积分兑换记录更新模型"""
    status: Optional[int] = None
    logistics_company: Optional[str] = None
    logistics_no: Optional[str] = None

class PointsExchangeResponse(PointsExchangeBase):
    """积分兑换记录响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
