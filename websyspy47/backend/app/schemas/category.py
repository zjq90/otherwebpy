from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ClothingCategoryBase(BaseModel):
    """衣物分类基础模型"""
    name: str = Field(..., max_length=50, description="分类名称")
    code: Optional[str] = Field(None, max_length=20, description="分类编码")
    parent_id: int = Field(0, description="父级分类ID")
    level: int = Field(1, description="分类层级")
    sort: int = Field(0, description="排序")
    icon: Optional[str] = Field(None, max_length=255, description="图标")
    description: Optional[str] = Field(None, description="描述")
    status: Optional[int] = Field(1, description="状态：0-禁用，1-启用")

class ClothingCategoryCreate(ClothingCategoryBase):
    """衣物分类创建模型"""
    pass

class ClothingCategoryUpdate(BaseModel):
    """衣物分类更新模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    sort: Optional[int] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None

class ClothingCategoryResponse(ClothingCategoryBase):
    """衣物分类响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PricingRuleBase(BaseModel):
    """计价规则基础模型"""
    category_id: int
    category_name: Optional[str] = None
    pricing_type: int = Field(1, description="计价方式：0-按件，1-按斤")
    unit_price: Decimal = Field(Decimal('0.00'), description="单价(元/件)")
    weight_price: Decimal = Field(Decimal('0.00'), description="单价(元/公斤)")
    has_min_price: int = Field(0, description="是否启用兜底价格")
    min_price_per_item: Decimal = Field(Decimal('0.00'), description="每件兜底价格(元)")
    points_per_unit: int = Field(0, description="每件/每公斤积分")
    status: Optional[int] = Field(1, description="状态：0-禁用，1-启用")
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

class PricingRuleCreate(PricingRuleBase):
    """计价规则创建模型"""
    pass

class PricingRuleUpdate(BaseModel):
    """计价规则更新模型"""
    category_name: Optional[str] = None
    pricing_type: Optional[int] = None
    unit_price: Optional[Decimal] = None
    weight_price: Optional[Decimal] = None
    has_min_price: Optional[int] = None
    min_price_per_item: Optional[Decimal] = None
    points_per_unit: Optional[int] = None
    status: Optional[int] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None

class PricingRuleResponse(PricingRuleBase):
    """计价规则响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
