from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClothingType(str, Enum):
    SHIRT = "上衣"
    PANTS = "裤子"
    DRESS = "裙子"
    COAT = "外套"
    SHOES = "鞋子"
    BAG = "包包"
    OTHER = "其他"


class OrderBase(BaseModel):
    user_name: str = Field(..., max_length=50, description="用户姓名")
    user_phone: str = Field(..., max_length=20, description="用户电话")
    address: str = Field(..., max_length=255, description="详细地址")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    district: Optional[str] = Field(None, max_length=50, description="区县")
    latitude: Optional[float] = Field(None, description="纬度")
    longitude: Optional[float] = Field(None, description="经度")
    clothing_types: Optional[str] = Field(None, description="衣物类型(多个用逗号分隔)")
    estimated_weight: Optional[float] = Field(None, description="预估重量(kg)")
    estimated_quantity: Optional[int] = Field(None, description="预估数量(件)")
    description: Optional[str] = Field(None, description="补充说明")
    appointment_time: Optional[datetime] = Field(None, description="预约时间")


class OrderCreate(OrderBase):
    pass


class OrderAccept(BaseModel):
    order_id: int = Field(..., description="订单ID")


class OrderReject(BaseModel):
    order_id: int = Field(..., description="订单ID")
    reject_reason: str = Field(..., description="拒绝原因")


class OrderComplete(BaseModel):
    order_id: int = Field(..., description="订单ID")
    actual_weight: float = Field(..., gt=0, description="实际重量(kg)")
    actual_quantity: Optional[int] = Field(None, description="实际数量(件)")
    recycle_photos: Optional[str] = Field(None, description="回收照片URL(多个用逗号分隔)")
    unit_price: float = Field(default=2.0, gt=0, description="单价(元/kg)")


class OrderResponse(OrderBase):
    id: int
    order_no: str
    collector_id: Optional[int]
    actual_weight: Optional[float]
    actual_quantity: Optional[int]
    recycle_photos: Optional[str]
    unit_price: float
    total_amount: Optional[float]
    status: OrderStatus
    reject_reason: Optional[str]
    cancel_reason: Optional[str]
    accepted_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    total: int
    orders: List[OrderResponse]


class OrderLogResponse(BaseModel):
    id: int
    order_id: int
    operator_type: str
    operator_id: Optional[int]
    action: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class RoutePoint(BaseModel):
    order_id: int
    order_no: str
    user_name: str
    address: str
    latitude: Optional[float]
    longitude: Optional[float]
    estimated_weight: Optional[float]


class RoutePlanResponse(BaseModel):
    total_distance: float
    total_duration: float
    points: List[RoutePoint]
    optimized_order: List[int]
