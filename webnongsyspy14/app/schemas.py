from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List, Any
from decimal import Decimal
import re

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    specification: str = Field(..., max_length=50, description="规格")
    grade: str = Field(..., max_length=20, description="等级")
    production_date: date = Field(..., description="生产日期")
    shelf_life: int = Field(..., ge=1, description="保质期（天）")
    suggested_retail_price: Decimal = Field(..., ge=0, description="建议零售价")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    specification: Optional[str] = Field(None, max_length=50)
    grade: Optional[str] = Field(None, max_length=20)
    production_date: Optional[date] = None
    shelf_life: Optional[int] = Field(None, ge=1)
    suggested_retail_price: Optional[Decimal] = Field(None, ge=0)

class Product(ProductBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductList(BaseModel):
    products: List[Product]
    total: int

class CustomerBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100, 
        description="客户名称（2-100个字符）"
    )
    phone: str = Field(
        ..., 
        min_length=7, 
        max_length=20, 
        description="联系电话（7-20个字符）"
    )
    email: Optional[str] = Field(
        None, 
        max_length=100, 
        description="电子邮箱（最多100个字符）"
    )
    address: Optional[str] = Field(
        None, 
        max_length=200, 
        description="地址（最多200个字符）"
    )
    contact_person: Optional[str] = Field(
        None, 
        max_length=50, 
        description="联系人（最多50个字符）"
    )
    preferences: Optional[str] = Field(
        None, 
        description="购买偏好"
    )
    status: str = Field(
        default="active", 
        description="状态: active/inactive"
    )
    
    @field_validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('客户名称至少需要2个字符')
        if len(v.strip()) > 100:
            raise ValueError('客户名称不能超过100个字符')
        return v.strip()
    
    @field_validator('phone')
    def validate_phone(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('联系电话不能为空')
        
        if len(v) < 7 or len(v) > 20:
            raise ValueError('联系电话长度应在7-20个字符之间')
        
        mobile_pattern = r'^1[3-9]\d{9}$'
        landline_pattern = r'^0\d{2,3}-?\d{7,8}$'
        landline_without_hyphen = r'^0\d{9,11}$'
        pure_digits = r'^\d{7,11}$'
        
        if (re.match(mobile_pattern, v) or 
            re.match(landline_pattern, v) or 
            re.match(landline_without_hyphen, v) or
            re.match(pure_digits, v)):
            return v
        else:
            raise ValueError('请输入有效的手机号码（11位）或固定电话（如：010-12345678）')
    
    @field_validator('email')
    def validate_email(cls, v):
        if v is None or v == '':
            return None
        v = v.strip()
        if not v:
            return None
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, v):
            return v
        else:
            raise ValueError('请输入有效的电子邮箱地址')
    
    @field_validator('status')
    def validate_status(cls, v):
        if v is None:
            return "active"
        valid_statuses = ['active', 'inactive']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下值之一: {valid_statuses}')
        return v
    
    @field_validator('address')
    def validate_address(cls, v):
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > 200:
            raise ValueError('地址不能超过200个字符')
        return v
    
    @field_validator('contact_person')
    def validate_contact_person(cls, v):
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > 50:
            raise ValueError('联系人姓名不能超过50个字符')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100
    )
    phone: Optional[str] = Field(
        None, 
        min_length=7, 
        max_length=20
    )
    email: Optional[str] = Field(
        None, 
        max_length=100
    )
    address: Optional[str] = Field(
        None, 
        max_length=200
    )
    contact_person: Optional[str] = Field(
        None, 
        max_length=50
    )
    preferences: Optional[str] = None
    status: Optional[str] = None
    
    @field_validator('name')
    def validate_name_update(cls, v):
        if v is None:
            return None
        return CustomerBase.validate_name(v)
    
    @field_validator('phone')
    def validate_phone_update(cls, v):
        if v is None:
            return None
        return CustomerBase.validate_phone(v)
    
    @field_validator('email')
    def validate_email_update(cls, v):
        return CustomerBase.validate_email(v)
    
    @field_validator('status')
    def validate_status_update(cls, v):
        return CustomerBase.validate_status(v)
    
    @field_validator('address')
    def validate_address_update(cls, v):
        return CustomerBase.validate_address(v)
    
    @field_validator('contact_person')
    def validate_contact_person_update(cls, v):
        return CustomerBase.validate_contact_person(v)

class Customer(CustomerBase):
    id: int
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True

class CustomerList(BaseModel):
    customers: List[Customer]
    total: int

class OrderItemBase(BaseModel):
    product_id: int = Field(..., ge=1, description="产品ID")
    product_name: str = Field(..., max_length=100, description="产品名称")
    quantity: int = Field(..., ge=1, description="数量")
    unit_price: Decimal = Field(..., ge=0, description="单价")
    subtotal: Decimal = Field(..., ge=0, description="小计")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_id: int = Field(..., ge=1, description="客户ID")
    customer_name: str = Field(..., max_length=100, description="客户名称")
    customer_phone: str = Field(..., max_length=20, description="客户电话")
    total_amount: Decimal = Field(..., ge=0, description="订单总金额")
    shipping_status: str = Field(default="pending", description="发货状态: pending/shipped/delivered")

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    estimated_delivery_date: Optional[date] = None
    order_date: Optional[date] = None

class OrderUpdate(BaseModel):
    customer_id: Optional[int] = Field(None, ge=1)
    customer_name: Optional[str] = Field(None, max_length=100)
    customer_phone: Optional[str] = Field(None, max_length=20)
    total_amount: Optional[Decimal] = Field(None, ge=0)
    shipping_status: Optional[str] = None
    order_date: Optional[date] = None
    estimated_delivery_date: Optional[date] = None

class Order(OrderBase):
    id: int
    order_date: date
    estimated_delivery_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItem] = []

    class Config:
        from_attributes = True

class OrderList(BaseModel):
    orders: List[Order]
    total: int

class ContractBase(BaseModel):
    order_id: int = Field(..., ge=1, description="订单ID")
    contract_number: str = Field(..., max_length=50, description="合同编号")
    contract_date: date = Field(..., description="合同日期")
    party_a: str = Field(..., max_length=200, description="甲方")
    party_b: str = Field(..., max_length=200, description="乙方")
    contract_content: str = Field(..., description="合同内容")
    status: str = Field(default="draft", description="状态: draft/signed/cancelled")

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    contract_number: Optional[str] = Field(None, max_length=50)
    contract_date: Optional[date] = None
    party_a: Optional[str] = Field(None, max_length=200)
    party_b: Optional[str] = Field(None, max_length=200)
    contract_content: Optional[str] = None
    status: Optional[str] = None
    signed_date: Optional[date] = None

class Contract(ContractBase):
    id: int
    signed_date: Optional[date] = None
    created_at: Optional[date] = None

    class Config:
        from_attributes = True

class ContractList(BaseModel):
    contracts: List[Contract]
    total: int

class LogisticsBase(BaseModel):
    order_id: int = Field(..., ge=1, description="订单ID")
    tracking_number: str = Field(..., max_length=50, description="物流单号")
    logistics_company: str = Field(..., max_length=100, description="物流公司")
    current_status: str = Field(default="待发货", description="当前状态")
    current_location: Optional[str] = Field(None, max_length=200, description="当前位置")
    estimated_arrival: Optional[date] = Field(None, description="预计到达时间")

class LogisticsCreate(LogisticsBase):
    pass

class LogisticsUpdate(BaseModel):
    tracking_number: Optional[str] = Field(None, max_length=50)
    logistics_company: Optional[str] = Field(None, max_length=100)
    current_status: Optional[str] = None
    current_location: Optional[str] = Field(None, max_length=200)
    estimated_arrival: Optional[date] = None

class Logistics(LogisticsBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LogisticsList(BaseModel):
    logistics: List[Logistics]
    total: int

class LogisticsTrackBase(BaseModel):
    logistics_id: int = Field(..., ge=1, description="物流ID")
    status: str = Field(..., max_length=50, description="状态")
    location: str = Field(..., max_length=200, description="位置")
    description: Optional[str] = Field(None, description="描述")

class LogisticsTrackCreate(LogisticsTrackBase):
    track_time: Optional[datetime] = None

class LogisticsTrack(LogisticsTrackBase):
    id: int
    track_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class PurchaseHistoryBase(BaseModel):
    customer_id: int = Field(..., ge=1, description="客户ID")
    order_id: int = Field(..., ge=1, description="订单ID")
    product_id: int = Field(..., ge=1, description="产品ID")
    product_name: str = Field(..., max_length=100, description="产品名称")
    quantity: int = Field(..., ge=1, description="数量")
    unit_price: Decimal = Field(..., ge=0, description="单价")
    purchase_date: date = Field(..., description="购买日期")

class PurchaseHistoryCreate(PurchaseHistoryBase):
    pass

class PurchaseHistory(PurchaseHistoryBase):
    id: int

    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    customer_id: int = Field(..., ge=1, description="客户ID")
    order_id: Optional[int] = Field(None, ge=1, description="订单ID")
    feedback_type: str = Field(..., max_length=20, description="反馈类型: suggestion/complaint/praise")
    content: str = Field(..., description="反馈内容")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分 1-5")

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    feedback_type: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    response: Optional[str] = None
    status: Optional[str] = None

class Feedback(FeedbackBase):
    id: int
    feedback_date: date
    customer_name: Optional[str] = None
    response: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FeedbackList(BaseModel):
    feedbacks: List[Feedback]
    total: int
