from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    id: int
    total_orders: int
    total_weight: float
    total_income: float
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    id_card: Optional[str] = Field(None, max_length=20, description="身份证号")


class UserStats(BaseModel):
    total_orders: int = Field(..., description="总完成订单数")
    total_weight: float = Field(..., description="总回收重量(kg)")
    total_income: float = Field(..., description="总收益(元)")
    today_orders: int = Field(..., description="今日完成订单数")
    today_weight: float = Field(..., description="今日回收重量(kg)")
    today_income: float = Field(..., description="今日收益(元)")


class WithdrawalCreate(BaseModel):
    amount: float = Field(..., gt=0, description="提现金额(元)")
    bank_card: str = Field(..., max_length=50, description="银行卡号")
    bank_name: str = Field(..., max_length=50, description="银行名称")
    account_name: str = Field(..., max_length=50, description="账户名")


class WithdrawalResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    bank_card: str
    bank_name: str
    account_name: str
    status: str
    reject_reason: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
