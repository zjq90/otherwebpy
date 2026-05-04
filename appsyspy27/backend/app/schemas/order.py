"""
订单数据验证模块
定义订单、支付、消费记录相关的请求和响应数据结构
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class OrderBase(BaseModel):
    """订单基础模型"""
    order_type: str = Field(..., max_length=20, description="订单类型")
    title: str = Field(..., max_length=200, description="订单标题")
    description: Optional[str] = Field(None, description="订单描述")


class OrderCreate(BaseModel):
    """订单创建模型"""
    order_type: str = Field(..., max_length=20, description="订单类型")
    card_type_id: Optional[int] = Field(None, description="卡类型ID")
    goods_id: Optional[int] = Field(None, description="商品ID")
    quantity: int = Field(default=1, ge=1, description="数量")
    promotion_id: Optional[int] = Field(None, description="优惠活动ID")


class OrderResponse(BaseModel):
    """订单响应模型"""
    id: int = Field(..., description="订单ID")
    order_no: str = Field(..., description="订单号")
    user_id: int = Field(..., description="用户ID")
    order_type: str = Field(..., description="订单类型")
    card_type_id: Optional[int] = Field(None, description="卡类型ID")
    goods_id: Optional[int] = Field(None, description="商品ID")
    title: str = Field(..., description="订单标题")
    description: Optional[str] = Field(None, description="订单描述")
    quantity: int = Field(..., description="数量")
    unit_price: Decimal = Field(..., description="单价")
    original_amount: Decimal = Field(..., description="原价总额")
    discount_amount: Decimal = Field(..., description="优惠金额")
    pay_amount: Decimal = Field(..., description="实付金额")
    pay_method: Optional[str] = Field(None, description="支付方式")
    third_pay_no: Optional[str] = Field(None, description="第三方支付单号")
    status: str = Field(..., description="订单状态")
    pay_time: Optional[datetime] = Field(None, description="支付时间")
    cancel_time: Optional[datetime] = Field(None, description="取消时间")
    promotion_id: Optional[int] = Field(None, description="优惠活动ID")
    contract_id: Optional[int] = Field(None, description="电子合同ID")
    remark: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """支付请求模型"""
    order_id: int = Field(..., description="订单ID")
    pay_method: str = Field(..., max_length=20, description="支付方式")


class PaymentResponse(BaseModel):
    """支付响应模型"""
    order_id: int = Field(..., description="订单ID")
    order_no: str = Field(..., description="订单号")
    pay_amount: Decimal = Field(..., description="支付金额")
    pay_method: str = Field(..., description="支付方式")
    pay_params: dict = Field(..., description="支付参数（用于前端唤起支付）")
    status: str = Field(..., description="支付状态")


class ConsumptionRecordResponse(BaseModel):
    """消费记录响应模型"""
    id: int = Field(..., description="记录ID")
    user_id: int = Field(..., description="用户ID")
    record_type: str = Field(..., description="消费类型")
    order_id: Optional[int] = Field(None, description="订单ID")
    user_card_id: Optional[int] = Field(None, description="用户卡ID")
    title: str = Field(..., description="消费标题")
    description: Optional[str] = Field(None, description="消费描述")
    amount: Decimal = Field(..., description="金额")
    balance_before: Optional[Decimal] = Field(None, description="消费前余额")
    balance_after: Optional[Decimal] = Field(None, description="消费后余额")
    count_before: Optional[int] = Field(None, description="扣次前次数")
    count_after: Optional[int] = Field(None, description="扣次后次数")
    duration_used: Optional[int] = Field(None, description="消耗时长")
    store_name: Optional[str] = Field(None, description="消费门店")
    operator_name: Optional[str] = Field(None, description="操作人")
    remark: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="消费时间")
    
    class Config:
        from_attributes = True


class PromotionResponse(BaseModel):
    """优惠活动响应模型"""
    id: int = Field(..., description="活动ID")
    name: str = Field(..., description="活动名称")
    code: Optional[str] = Field(None, description="活动编码")
    promotion_type: str = Field(..., description="活动类型")
    description: Optional[str] = Field(None, description="活动描述")
    applicable_card_types: Optional[str] = Field(None, description="适用卡类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    discount_config: str = Field(..., description="优惠配置")
    sort_order: int = Field(..., description="排序权重")
    is_active: bool = Field(..., description="是否启用")
    
    class Config:
        from_attributes = True


class MonthlyBillResponse(BaseModel):
    """月度账单响应模型"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    total_amount: Decimal = Field(..., description="总金额")
    total_count: int = Field(..., description="消费笔数")
    records: List[ConsumptionRecordResponse] = Field(..., description="消费记录列表")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int = Field(..., description="总条数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total_pages: int = Field(..., description="总页数")
