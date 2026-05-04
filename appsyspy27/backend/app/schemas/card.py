"""
会员卡数据验证模块
定义会员卡相关的请求和响应数据结构
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class CardTypeBase(BaseModel):
    """会员卡类型基础模型"""
    name: str = Field(..., max_length=100, description="卡类型名称")
    code: str = Field(..., max_length=50, description="卡类型编码")
    description: Optional[str] = Field(None, description="卡类型描述")
    category: str = Field(..., max_length=20, description="卡类型分类")
    original_price: Decimal = Field(..., gt=0, description="原价")
    current_price: Decimal = Field(..., gt=0, description="当前售价")
    valid_days: Optional[int] = Field(None, gt=0, description="有效期天数")
    total_count: Optional[int] = Field(None, gt=0, description="总次数")
    total_duration: Optional[int] = Field(None, gt=0, description="总时长（分钟）")
    usage_scope: Optional[str] = Field(None, description="使用范围")
    is_on_sale: bool = Field(default=True, description="是否上架")


class CardTypeResponse(CardTypeBase):
    """会员卡类型响应模型"""
    id: int = Field(..., description="卡类型ID")
    sort_order: int = Field(..., description="排序权重")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class UserCardBase(BaseModel):
    """用户会员卡基础模型"""
    display_name: Optional[str] = Field(None, max_length=100, description="卡显示名称")


class UserCardCreate(BaseModel):
    """用户会员卡创建模型"""
    user_id: int = Field(..., description="用户ID")
    card_type_id: int = Field(..., description="卡类型ID")
    order_id: Optional[int] = Field(None, description="订单ID")


class UserCardUpdate(BaseModel):
    """用户会员卡更新模型"""
    display_name: Optional[str] = Field(None, max_length=100, description="卡显示名称")
    remark: Optional[str] = Field(None, description="备注")


class UserCardResponse(BaseModel):
    """用户会员卡响应模型"""
    id: int = Field(..., description="用户卡ID")
    user_id: int = Field(..., description="用户ID")
    card_type_id: int = Field(..., description="卡类型ID")
    card_number: str = Field(..., description="卡号")
    display_name: Optional[str] = Field(None, description="卡显示名称")
    card_type_name: str = Field(..., description="卡类型名称")
    card_category: str = Field(..., description="卡类型分类")
    
    purchase_time: Optional[datetime] = Field(None, description="购买时间")
    activate_time: Optional[datetime] = Field(None, description="激活时间")
    expire_time: Optional[date] = Field(None, description="过期时间")
    
    remaining_count: Optional[int] = Field(None, description="剩余次数")
    total_count: Optional[int] = Field(None, description="总次数")
    remaining_duration: Optional[int] = Field(None, description="剩余时长")
    total_duration: Optional[int] = Field(None, description="总时长")
    
    status: str = Field(..., description="卡状态")
    is_valid: bool = Field(..., description="是否有效")
    usage_scope: Optional[str] = Field(None, description="使用范围")
    
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class CardUsageRecord(BaseModel):
    """卡使用记录模型"""
    id: int = Field(..., description="记录ID")
    title: str = Field(..., description="标题")
    record_type: str = Field(..., description="类型")
    count_before: Optional[int] = Field(None, description="使用前次数")
    count_after: Optional[int] = Field(None, description="使用后次数")
    duration_used: Optional[int] = Field(None, description="使用时长")
    store_name: Optional[str] = Field(None, description="门店")
    operator_name: Optional[str] = Field(None, description="操作人")
    created_at: datetime = Field(..., description="时间")
    
    class Config:
        from_attributes = True
