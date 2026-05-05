"""
订单相关的Pydantic模型
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== 衣物类型模型 ====================

class ClothingTypeResponse(BaseModel):
    """
    衣物类型响应
    """
    id: int
    name: str
    code: str
    description: Optional[str]
    icon: Optional[str]
    points_per_unit: int
    carbon_per_unit: float
    
    class Config:
        from_attributes = True


# ==================== 回收人员模型 ====================

class CollectorResponse(BaseModel):
    """
    回收人员响应
    """
    id: int
    name: str
    phone: str
    avatar: Optional[str]
    work_status: int
    rating: float
    total_orders: int
    latitude: Optional[float]
    longitude: Optional[float]
    
    class Config:
        from_attributes = True


# ==================== 预约订单模型 ====================

class CreateOrderRequest(BaseModel):
    """
    创建预约订单请求
    """
    clothing_type_id: int = Field(..., description="衣物类型ID")
    quantity: int = Field(..., ge=1, description="数量")
    quality: str = Field(default="普通", description="品质：优质、普通、较差")
    
    # 地址信息
    province: Optional[str] = Field(None, description="省")
    city: Optional[str] = Field(None, description="市")
    district: Optional[str] = Field(None, description="区")
    address: str = Field(..., description="详细地址")
    contact_name: str = Field(..., description="联系人姓名")
    contact_phone: str = Field(..., min_length=11, description="联系电话")
    
    # 时间信息
    scheduled_date: str = Field(..., description="预约日期，格式：YYYY-MM-DD")
    scheduled_time_slot: str = Field(..., description="预约时间段")
    
    remark: Optional[str] = Field(None, description="备注")


class OrderResponse(BaseModel):
    """
    订单响应
    """
    id: int
    order_no: str
    user_id: int
    collector_id: Optional[int]
    clothing_type_id: int
    clothing_name: Optional[str]
    quantity: int
    unit: str
    quality: str
    
    # 地址
    province: Optional[str]
    city: Optional[str]
    district: Optional[str]
    address: str
    full_address: str
    contact_name: str
    contact_phone: str
    
    # 时间
    scheduled_date: str
    scheduled_time_slot: str
    estimated_arrival: Optional[str]
    actual_arrival_time: Optional[datetime]
    complete_time: Optional[datetime]
    cancel_time: Optional[datetime]
    cancel_reason: Optional[str]
    
    # 状态和积分
    status: int
    status_text: str
    points_earned: int
    carbon_earned: float
    
    remark: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    
    # 关联信息
    collector: Optional[CollectorResponse] = None
    
    class Config:
        from_attributes = True


class OrderStatusHistoryResponse(BaseModel):
    """
    订单状态历史响应
    """
    id: int
    order_id: int
    order_no: Optional[str]
    status: int
    status_text: Optional[str]
    operator_type: Optional[str]
    operator_id: Optional[int]
    remark: Optional[str]
    create_time: Optional[datetime]
    
    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """
    订单详情响应（包含状态历史）
    """
    status_histories: list[OrderStatusHistoryResponse] = []


class CancelOrderRequest(BaseModel):
    """
    取消订单请求
    """
    cancel_reason: str = Field(..., description="取消原因")


class UpdateTimeSlotRequest(BaseModel):
    """
    调整预约时间请求
    """
    scheduled_date: str = Field(..., description="新的预约日期")
    scheduled_time_slot: str = Field(..., description="新的预约时间段")


# ==================== 回收流程模型 ====================

class RecycleProcessResponse(BaseModel):
    """
    回收流程响应
    """
    id: int
    step: int
    title: str
    description: Optional[str]
    icon: Optional[str]
    image: Optional[str]
    
    class Config:
        from_attributes = True
