"""
Pydantic数据模型定义
用于API请求和响应的数据验证
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class BillingCycle(str, Enum):
    """计费周期枚举"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class BillingType(str, Enum):
    """计费标准类型枚举"""
    AREA = "area"
    UNIT = "unit"
    FIXED = "fixed"


class BillStatus(str, Enum):
    """账单状态枚举"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """支付方式枚举"""
    CASH = "cash"
    WECHAT = "wechat"
    ALIPAY = "alipay"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class ReminderMethod(str, Enum):
    """催缴方式枚举"""
    SMS = "sms"
    PHONE = "phone"
    NOTICE = "notice"
    WECHAT = "wechat"


class InvoiceType(str, Enum):
    """票据类型枚举"""
    RECEIPT = "receipt"
    INVOICE = "invoice"


class InvoiceStatus(str, Enum):
    """票据状态枚举"""
    PENDING = "pending"
    ISSUED = "issued"
    VOIDED = "voided"


# 费用项目相关模型
class FeeItemBase(BaseModel):
    """费用项目基础模型"""
    name: str = Field(..., max_length=100, description="费用项目名称")
    code: str = Field(..., max_length=50, description="费用项目编码")
    description: Optional[str] = Field(None, description="费用项目描述")
    billing_cycle: BillingCycle = Field(default=BillingCycle.MONTHLY, description="计费周期")
    billing_type: BillingType = Field(default=BillingType.AREA, description="计费标准类型")
    unit_price: Decimal = Field(default=0, ge=0, description="单位价格")
    is_active: bool = Field(default=True, description="是否启用")


class FeeItemCreate(FeeItemBase):
    """创建费用项目模型"""
    pass


class FeeItemUpdate(BaseModel):
    """更新费用项目模型"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    billing_cycle: Optional[BillingCycle] = None
    billing_type: Optional[BillingType] = None
    unit_price: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class FeeItem(FeeItemBase):
    """费用项目响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 房产信息相关模型
class PropertyBase(BaseModel):
    """房产信息基础模型"""
    property_number: str = Field(..., max_length=50, description="房产编号")
    building: Optional[str] = Field(None, max_length=50, description="楼栋号")
    unit: Optional[str] = Field(None, max_length=50, description="单元号")
    room_number: Optional[str] = Field(None, max_length=50, description="房间号")
    area: Decimal = Field(default=0, ge=0, description="建筑面积")
    property_type: str = Field(default="住宅", max_length=50, description="房产类型")
    owner_name: Optional[str] = Field(None, max_length=100, description="业主姓名")
    owner_phone: Optional[str] = Field(None, max_length=20, description="业主电话")
    owner_id_card: Optional[str] = Field(None, max_length=20, description="业主身份证号")
    is_occupied: bool = Field(default=True, description="是否入住")
    move_in_date: Optional[date] = Field(None, description="入住日期")
    is_active: bool = Field(default=True, description="是否启用")
    remark: Optional[str] = Field(None, description="备注")


class PropertyCreate(PropertyBase):
    """创建房产信息模型"""
    pass


class PropertyUpdate(BaseModel):
    """更新房产信息模型"""
    building: Optional[str] = None
    unit: Optional[str] = None
    room_number: Optional[str] = None
    area: Optional[Decimal] = Field(None, ge=0)
    property_type: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_id_card: Optional[str] = None
    is_occupied: Optional[bool] = None
    move_in_date: Optional[date] = None
    is_active: Optional[bool] = None
    remark: Optional[str] = None


class Property(PropertyBase):
    """房产信息响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 账单相关模型
class BillBase(BaseModel):
    """账单基础模型"""
    property_id: int = Field(..., description="房产ID")
    fee_item_id: int = Field(..., description="费用项目ID")
    billing_year: int = Field(..., description="计费年份")
    billing_month: int = Field(..., ge=1, le=12, description="计费月份")
    amount: Decimal = Field(default=0, ge=0, description="账单金额")
    status: BillStatus = Field(default=BillStatus.PENDING, description="账单状态")
    due_date: Optional[date] = Field(None, description="缴费截止日期")
    remark: Optional[str] = Field(None, description="备注")


class BillCreate(BillBase):
    """创建账单模型"""
    pass


class BillUpdate(BaseModel):
    """更新账单模型"""
    status: Optional[BillStatus] = None
    due_date: Optional[date] = None
    remark: Optional[str] = None


class BillPayment(BaseModel):
    """账单支付模型"""
    amount: Decimal = Field(..., ge=0, description="支付金额")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH, description="支付方式")
    transaction_id: Optional[str] = Field(None, description="交易流水号")
    collector: Optional[str] = Field(None, description="收款人")


class Bill(BillBase):
    """账单响应模型"""
    id: int
    bill_number: str
    paid_amount: Decimal
    generated_at: datetime
    paid_at: Optional[datetime]
    payment_method: Optional[str]
    created_at: datetime
    updated_at: datetime
    property_info: Optional[Property] = None
    fee_item_info: Optional[FeeItem] = None

    class Config:
        from_attributes = True


# 缴费记录相关模型
class PaymentRecordBase(BaseModel):
    """缴费记录基础模型"""
    bill_id: int = Field(..., description="账单ID")
    amount: Decimal = Field(..., ge=0, description="缴费金额")
    payment_method: PaymentMethod = Field(default=PaymentMethod.CASH, description="支付方式")
    transaction_id: Optional[str] = Field(None, description="交易流水号")
    collector: Optional[str] = Field(None, description="收款人")
    remark: Optional[str] = Field(None, description="备注")


class PaymentRecordCreate(PaymentRecordBase):
    """创建缴费记录模型"""
    pass


class PaymentRecord(PaymentRecordBase):
    """缴费记录响应模型"""
    id: int
    record_number: str
    paid_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 催缴记录相关模型
class ReminderBase(BaseModel):
    """催缴记录基础模型"""
    bill_id: int = Field(..., description="账单ID")
    method: ReminderMethod = Field(default=ReminderMethod.NOTICE, description="催缴方式")
    content: Optional[str] = Field(None, description="催缴内容")
    operator: Optional[str] = Field(None, description="执行人")
    remark: Optional[str] = Field(None, description="备注")


class ReminderCreate(ReminderBase):
    """创建催缴记录模型"""
    pass


class Reminder(ReminderBase):
    """催缴记录响应模型"""
    id: int
    reminder_count: int
    reminded_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 票据相关模型
class InvoiceBase(BaseModel):
    """票据基础模型"""
    bill_id: int = Field(..., description="账单ID")
    invoice_type: InvoiceType = Field(default=InvoiceType.RECEIPT, description="票据类型")
    amount: Decimal = Field(default=0, ge=0, description="票据金额")
    invoice_title: Optional[str] = Field(None, max_length=200, description="发票抬头")
    tax_number: Optional[str] = Field(None, max_length=50, description="税号")
    issuer: Optional[str] = Field(None, description="开票人")
    status: InvoiceStatus = Field(default=InvoiceStatus.PENDING, description="票据状态")
    remark: Optional[str] = Field(None, description="备注")


class InvoiceCreate(InvoiceBase):
    """创建票据模型"""
    pass


class Invoice(InvoiceBase):
    """票据响应模型"""
    id: int
    invoice_number: str
    issued_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 批量账单生成模型
class BatchBillGenerate(BaseModel):
    """批量生成账单模型"""
    billing_year: int = Field(..., description="计费年份")
    billing_month: int = Field(..., ge=1, le=12, description="计费月份")
    fee_item_ids: Optional[List[int]] = Field(None, description="费用项目ID列表，不传则生成所有启用项目的账单")
    property_ids: Optional[List[int]] = Field(None, description="房产ID列表，不传则生成所有启用房产的账单")


# 财务统计模型
class FinancialStats(BaseModel):
    """财务统计模型"""
    total_bills: int = 0
    total_amount: Decimal = Decimal(0)
    paid_amount: Decimal = Decimal(0)
    unpaid_amount: Decimal = Decimal(0)
    overdue_amount: Decimal = Decimal(0)


# 分页响应模型
class PageResponse(BaseModel):
    """分页响应模型"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
