"""
销售模块Pydantic schemas
用于API的数据验证和序列化
"""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime
from app.validators import is_valid_phone, is_valid_email


# 客户相关schemas
class CustomerBase(BaseModel):
    """
    客户基础schema
    """
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('客户名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('客户名称长度不能超过100个字符')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 254:
            raise ValueError('邮箱长度不能超过254个字符')
        if not is_valid_email(v):
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('contact_person')
    @classmethod
    def validate_contact_person(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError('联系人姓名长度不能超过50个字符')
        return v

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('地址长度不能超过500个字符')
        return v


class CustomerCreate(CustomerBase):
    """
    客户创建schema
    """
    pass


class CustomerUpdate(CustomerBase):
    """
    客户更新schema
    """
    name: Optional[str] = None


class CustomerResponse(CustomerBase):
    """
    客户响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 订单明细相关schemas
class OrderItemBase(BaseModel):
    """
    订单明细基础schema
    """
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('数量不能为空')
        if v < 1:
            raise ValueError('数量必须大于0')
        if v > 1000000:
            raise ValueError('数量不能超过1000000')
        return v

    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('单价不能为空')
        if v < 0:
            raise ValueError('单价不能为负数')
        if v > 1000000000:
            raise ValueError('单价不能超过1000000000')
        return round(v, 2)

    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('总价不能为空')
        if v < 0:
            raise ValueError('总价不能为负数')
        if v > 10000000000:
            raise ValueError('总价不能超过10000000000')
        return round(v, 2)


class OrderItemCreate(OrderItemBase):
    """
    订单明细创建schema
    """
    pass


class OrderItemUpdate(BaseModel):
    """
    订单明细更新schema
    """
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

    @field_validator('quantity')
    @classmethod
    def validate_quantity_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 1:
            raise ValueError('数量必须大于0')
        if v > 1000000:
            raise ValueError('数量不能超过1000000')
        return v

    @field_validator('unit_price')
    @classmethod
    def validate_unit_price_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('单价不能为负数')
        if v > 1000000000:
            raise ValueError('单价不能超过1000000000')
        return round(v, 2)

    @field_validator('total_price')
    @classmethod
    def validate_total_price_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('总价不能为负数')
        if v > 10000000000:
            raise ValueError('总价不能超过10000000000')
        return round(v, 2)


class OrderItemResponse(OrderItemBase):
    """
    订单明细响应schema
    """
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 订单相关schemas
class OrderBase(BaseModel):
    """
    订单基础schema
    """
    customer_id: int
    total_amount: float
    status: str = "待处理"

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('订单金额不能为空')
        if v < 0:
            raise ValueError('订单金额不能为负数')
        if v > 100000000000:
            raise ValueError('订单金额不能超过100000000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待处理"
        v = v.strip()
        valid_statuses = ["待处理", "待发货", "已发货", "已完成", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'订单状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class OrderCreate(OrderBase):
    """
    订单创建schema
    """
    order_items: List[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    """
    订单更新schema
    """
    customer_id: Optional[int] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('订单金额不能为负数')
        if v > 100000000000:
            raise ValueError('订单金额不能超过100000000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待处理", "待发货", "已发货", "已完成", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'订单状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class OrderResponse(OrderBase):
    """
    订单响应schema
    """
    id: int
    order_no: str
    order_date: datetime
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse] = []
    customer: Optional[CustomerResponse] = None

    class Config:
        from_attributes = True
