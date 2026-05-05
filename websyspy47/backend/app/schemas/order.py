from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class OrderItemBase(BaseModel):
    """订单明细基础模型"""
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    pricing_type: int = Field(0, description="计价方式：0-按件，1-按斤")
    quantity: Optional[int] = None
    weight: Optional[Decimal] = None
    unit_price: Decimal = Field(..., description="单价")
    amount: Decimal = Field(..., description="小计金额")
    points: int = Field(0, description="获得积分")

class OrderItemCreate(OrderItemBase):
    """订单明细创建模型"""
    pass

class OrderItemResponse(OrderItemBase):
    """订单明细响应模型"""
    id: int
    order_id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    """订单基础模型"""
    user_id: int
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    address: str = Field(..., max_length=500, description="回收地址")
    area: Optional[str] = Field(None, max_length=100, description="区域")
    appointment_date: Optional[datetime] = None
    appointment_time: Optional[str] = Field(None, max_length=50, description="预约时间段")
    recycler_id: Optional[int] = None
    recycler_name: Optional[str] = None
    status: Optional[int] = Field(0, description="订单状态")
    remark: Optional[str] = None
    total_weight: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    total_points: Optional[int] = None

class OrderCreate(OrderBase):
    """订单创建模型"""
    order_no: str = Field(..., max_length=50, description="订单编号")
    items: List[OrderItemCreate] = []

class OrderUpdate(BaseModel):
    """订单更新模型"""
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    address: Optional[str] = None
    area: Optional[str] = None
    appointment_date: Optional[datetime] = None
    appointment_time: Optional[str] = None
    recycler_id: Optional[int] = None
    recycler_name: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None
    cancel_reason: Optional[str] = None
    exception_reason: Optional[str] = None
    total_weight: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    total_points: Optional[int] = None

class OrderResponse(OrderBase):
    """订单响应模型"""
    id: int
    order_no: str
    cancel_reason: Optional[str] = None
    exception_reason: Optional[str] = None
    accept_time: Optional[datetime] = None
    complete_time: Optional[datetime] = None
    cancel_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderStatistics(BaseModel):
    """订单统计模型"""
    total_orders: int = 0
    pending_orders: int = 0
    accepted_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    exception_orders: int = 0
    total_weight: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    complete_rate: Decimal = Decimal('0.00')

class DailyStatistics(BaseModel):
    """每日统计模型"""
    date: str
    order_count: int
    total_weight: Decimal
    total_amount: Decimal
