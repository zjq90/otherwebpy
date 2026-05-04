"""
卡项管理Pydantic Schema
定义卡类型和卡项的请求/响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CardTypeBase(BaseModel):
    """
    卡类型基础Schema
    包含卡类型的基本字段
    """
    name: str = Field(..., min_length=1, max_length=50, description="卡类型名称")
    code: str = Field(..., min_length=1, max_length=50, description="卡类型代码")
    description: Optional[str] = Field(None, description="卡类型描述")
    is_active: Optional[bool] = Field(True, description="是否启用")


class CardTypeCreate(CardTypeBase):
    """
    卡类型创建Schema
    继承自CardTypeBase，用于创建新的卡类型
    """
    pass


class CardTypeUpdate(BaseModel):
    """
    卡类型更新Schema
    所有字段都是可选的，用于部分更新
    """
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="卡类型名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="卡类型代码")
    description: Optional[str] = Field(None, description="卡类型描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class CardTypeResponse(CardTypeBase):
    """
    卡类型响应Schema
    包含卡类型的所有字段，用于返回给前端
    """
    id: int = Field(..., description="卡类型ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class CardBase(BaseModel):
    """
    卡项基础Schema
    包含卡项的基本字段
    """
    name: str = Field(..., min_length=1, max_length=100, description="卡项名称")
    card_type_id: int = Field(..., description="卡类型ID")
    price: float = Field(..., gt=0, description="价格")
    original_price: Optional[float] = Field(None, gt=0, description="原价")
    valid_days: Optional[int] = Field(None, ge=0, description="有效期天数")
    valid_count: Optional[int] = Field(None, ge=0, description="有效次数")
    stored_amount: Optional[float] = Field(None, ge=0, description="储值金额")
    bonus_amount: Optional[float] = Field(0, ge=0, description="赠送金额")
    benefits: Optional[str] = Field(None, description="包含权益")
    renewal_rules: Optional[str] = Field(None, description="续费规则")
    description: Optional[str] = Field(None, description="卡项描述")
    is_active: Optional[bool] = Field(True, description="是否启用")
    sort_order: Optional[int] = Field(0, description="排序权重")


class CardCreate(CardBase):
    """
    卡项创建Schema
    继承自CardBase，用于创建新的卡项
    """
    pass


class CardUpdate(BaseModel):
    """
    卡项更新Schema
    所有字段都是可选的，用于部分更新
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="卡项名称")
    card_type_id: Optional[int] = Field(None, description="卡类型ID")
    price: Optional[float] = Field(None, gt=0, description="价格")
    original_price: Optional[float] = Field(None, gt=0, description="原价")
    valid_days: Optional[int] = Field(None, ge=0, description="有效期天数")
    valid_count: Optional[int] = Field(None, ge=0, description="有效次数")
    stored_amount: Optional[float] = Field(None, ge=0, description="储值金额")
    bonus_amount: Optional[float] = Field(None, ge=0, description="赠送金额")
    benefits: Optional[str] = Field(None, description="包含权益")
    renewal_rules: Optional[str] = Field(None, description="续费规则")
    description: Optional[str] = Field(None, description="卡项描述")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort_order: Optional[int] = Field(None, description="排序权重")


class CardResponse(CardBase):
    """
    卡项响应Schema
    包含卡项的所有字段，用于返回给前端
    """
    id: int = Field(..., description="卡项ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    card_type: Optional[CardTypeResponse] = Field(None, description="关联的卡类型")
    
    class Config:
        from_attributes = True
