from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from .common import validate_phone, validate_id_card, validate_password

class RecyclerBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    id_card: Optional[str] = Field(None, max_length=18, description="身份证号")
    area: Optional[str] = Field(None, max_length=200, description="负责区域")
    status: Optional[int] = Field(1, description="状态：0-禁用，1-正常，2-休假")

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: str) -> str:
        return validate_phone(v)

    @field_validator('id_card')
    @classmethod
    def validate_id_card_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_id_card(v)

class RecyclerCreate(RecyclerBase):
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v, is_new=True)

class RecyclerUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    area: Optional[str] = None
    status: Optional[int] = None
    password: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('id_card')
    @classmethod
    def validate_id_card_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_id_card(v)

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return validate_password(v, is_new=False)

class RecyclerResponse(RecyclerBase):
    """回收人员响应模型"""
    id: int
    total_orders: int = 0
    completed_orders: int = 0
    total_weight: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    performance_score: Decimal = Decimal('100.00')
    performance_level: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RecyclerPerformanceBase(BaseModel):
    """绩效考核记录基础模型"""
    recycler_id: int
    period_type: str = Field(..., max_length=20, description="周期类型")
    period_year: int
    period_month: Optional[int] = None
    order_count: int = 0
    complete_rate: Decimal = Decimal('0.00')
    avg_response_time: int = 0
    user_satisfaction: Decimal = Decimal('5.00')
    score: Decimal = Decimal('0.00')
    level: Optional[str] = None
    comments: Optional[str] = None

class RecyclerPerformanceCreate(RecyclerPerformanceBase):
    """绩效考核记录创建模型"""
    pass

class RecyclerPerformanceResponse(RecyclerPerformanceBase):
    """绩效考核记录响应模型"""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
