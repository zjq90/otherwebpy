# -*- coding: utf-8 -*-
"""
试块数据模型
============
定义试块相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TestBlockBase(BaseModel):
    """试块基础模型"""
    block_no: str = Field(..., max_length=50, description="试块编号")
    batch_id: int = Field(..., description="生产批次ID")
    sample_date: date = Field(..., description="取样日期")
    casting_date: date = Field(..., description="成型日期")
    test_age: int = Field(..., ge=1, description="试验龄期(天)")
    planned_test_date: date = Field(..., description="计划试验日期")
    block_size: str = Field("150x150x150", max_length=50, description="试块规格")
    quantity: int = Field(3, ge=1, description="试块数量")
    curing_condition: str = Field("标准养护", max_length=50, description="养护条件")
    sample_location: Optional[str] = Field(None, max_length=100, description="取样部位")
    sampler: str = Field(..., max_length=50, description="取样人")
    remark: Optional[str] = Field(None, description="备注")
    status: str = Field("待试验", max_length=20, description="状态")


class TestBlockCreate(TestBlockBase):
    """试块创建模型"""
    pass


class TestBlockUpdate(BaseModel):
    """试块更新模型"""
    sample_date: Optional[date] = Field(None, description="取样日期")
    casting_date: Optional[date] = Field(None, description="成型日期")
    test_age: Optional[int] = Field(None, ge=1, description="试验龄期(天)")
    planned_test_date: Optional[date] = Field(None, description="计划试验日期")
    block_size: Optional[str] = Field(None, max_length=50, description="试块规格")
    quantity: Optional[int] = Field(None, ge=1, description="试块数量")
    curing_condition: Optional[str] = Field(None, max_length=50, description="养护条件")
    sample_location: Optional[str] = Field(None, max_length=100, description="取样部位")
    sampler: Optional[str] = Field(None, max_length=50, description="取样人")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="状态")


class TestBlockResponse(TestBlockBase):
    """试块响应模型"""
    id: int = Field(..., description="试块ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
