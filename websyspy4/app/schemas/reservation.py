"""
预约Pydantic模型
用于预约相关API的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class ReservationBase(BaseModel):
    """
    预约基础模型
    """
    product_id: int = Field(..., gt=0, description="产品ID")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    quantity: int = Field(1, ge=1, description="数量")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class ReservationCreate(ReservationBase):
    """
    预约创建模型
    """
    pass


class ReservationUpdate(BaseModel):
    """
    预约更新模型
    """
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    quantity: Optional[int] = Field(None, ge=1, description="数量")
    remark: Optional[str] = Field(None, max_length=500, description="备注")
    status: Optional[str] = Field(None, description="预约状态")


class ReservationResponse(ReservationBase):
    """
    预约响应模型
    """
    id: int
    reservation_no: str
    user_id: int
    rental_days: int
    daily_rent: Decimal
    total_rent: Decimal
    deposit: Decimal
    deposit_paid: bool
    deposit_paid_at: Optional[datetime] = None
    picked_up_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    status: str
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    product_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
