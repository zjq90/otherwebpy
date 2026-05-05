# -*- coding: utf-8 -*-
"""
结算单数据模型
==============
定义结算单相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SettlementOrderBase(BaseModel):
    """结算单基础模型"""
    settlement_no: str = Field(..., max_length=50, description="结算单号")
    supplier_id: int = Field(..., description="供应商ID")
    settlement_period: str = Field(..., max_length=50, description="结算周期")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    material_summary: Optional[str] = Field(None, description="材料汇总(JSON格式)")
    total_quantity: float = Field(..., ge=0, description="总数量")
    total_amount: float = Field(..., ge=0, description="总金额")
    discount_amount: Optional[float] = Field(None, ge=0, description="优惠金额")
    final_amount: float = Field(..., ge=0, description="应付金额")
    status: str = Field("待确认", max_length=20, description="状态")
    created_by: str = Field(..., max_length=50, description="制单人")
    created_date: date = Field(default_factory=date.today, description="制单日期")
    confirmed_by: Optional[str] = Field(None, max_length=50, description="确认人")
    confirm_date: Optional[date] = Field(None, description="确认日期")
    paid_by: Optional[str] = Field(None, max_length=50, description="付款人")
    paid_date: Optional[date] = Field(None, description="付款日期")
    remark: Optional[str] = Field(None, description="备注")


class SettlementOrderCreate(SettlementOrderBase):
    """结算单创建模型"""
    pass


class SettlementOrderUpdate(BaseModel):
    """结算单更新模型"""
    settlement_period: Optional[str] = Field(None, max_length=50, description="结算周期")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    material_summary: Optional[str] = Field(None, description="材料汇总(JSON格式)")
    total_quantity: Optional[float] = Field(None, ge=0, description="总数量")
    total_amount: Optional[float] = Field(None, ge=0, description="总金额")
    discount_amount: Optional[float] = Field(None, ge=0, description="优惠金额")
    final_amount: Optional[float] = Field(None, ge=0, description="应付金额")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    created_by: Optional[str] = Field(None, max_length=50, description="制单人")
    created_date: Optional[date] = Field(None, description="制单日期")
    confirmed_by: Optional[str] = Field(None, max_length=50, description="确认人")
    confirm_date: Optional[date] = Field(None, description="确认日期")
    paid_by: Optional[str] = Field(None, max_length=50, description="付款人")
    paid_date: Optional[date] = Field(None, description="付款日期")
    remark: Optional[str] = Field(None, description="备注")


class SettlementOrderResponse(SettlementOrderBase):
    """结算单响应模型"""
    id: int = Field(..., description="结算单ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
