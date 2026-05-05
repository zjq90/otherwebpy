# -*- coding: utf-8 -*-
"""
供应商数据模型
==============
定义供应商相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    """供应商基础模型"""
    name: str = Field(..., max_length=100, description="供应商名称")
    code: str = Field(..., max_length=50, description="供应商编码")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, description="地址")
    supplier_type: str = Field("原材料供应商", max_length=50, description="供应商类型")
    rating: Optional[float] = Field(None, ge=0, le=100, description="综合评分")
    rating_level: Optional[str] = Field(None, max_length=20, description="评级等级")
    status: bool = Field(True, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class SupplierCreate(SupplierBase):
    """供应商创建模型"""
    pass


class SupplierUpdate(BaseModel):
    """供应商更新模型"""
    name: Optional[str] = Field(None, max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, description="地址")
    supplier_type: Optional[str] = Field(None, max_length=50, description="供应商类型")
    rating: Optional[float] = Field(None, ge=0, le=100, description="综合评分")
    rating_level: Optional[str] = Field(None, max_length=20, description="评级等级")
    status: Optional[bool] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class SupplierResponse(SupplierBase):
    """供应商响应模型"""
    id: int = Field(..., description="供应商ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
