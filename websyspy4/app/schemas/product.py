"""
产品Pydantic模型
用于产品相关API的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    """
    产品基础模型
    """
    name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    category_id: int = Field(..., gt=0, description="分类ID")
    daily_rent: Decimal = Field(..., ge=0, description="日租金")
    deposit: Decimal = Field(..., ge=0, description="押金")
    stock_quantity: int = Field(1, ge=0, description="库存数量")
    available_quantity: int = Field(1, ge=0, description="可用数量")
    image_url: Optional[str] = Field(None, max_length=500, description="产品图片URL")
    status: int = Field(1, ge=1, le=2, description="状态：1-上架，2-下架")
    is_hot: bool = Field(False, description="是否热门")


class ProductCreate(ProductBase):
    """
    产品创建模型
    """
    pass


class ProductUpdate(BaseModel):
    """
    产品更新模型
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    category_id: Optional[int] = Field(None, gt=0, description="分类ID")
    daily_rent: Optional[Decimal] = Field(None, ge=0, description="日租金")
    deposit: Optional[Decimal] = Field(None, ge=0, description="押金")
    stock_quantity: Optional[int] = Field(None, ge=0, description="库存数量")
    available_quantity: Optional[int] = Field(None, ge=0, description="可用数量")
    image_url: Optional[str] = Field(None, max_length=500, description="产品图片URL")
    status: Optional[int] = Field(None, ge=1, le=2, description="状态")
    is_hot: Optional[bool] = Field(None, description="是否热门")


class ProductResponse(ProductBase):
    """
    产品响应模型
    """
    id: int
    category_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
