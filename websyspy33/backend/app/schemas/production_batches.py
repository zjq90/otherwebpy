# -*- coding: utf-8 -*-
"""
生产批次数据模型
================
定义生产批次相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductionBatchBase(BaseModel):
    """生产批次基础模型"""
    batch_no: str = Field(..., max_length=50, description="生产批号")
    mix_design_id: int = Field(..., description="配比设计ID")
    project_name: str = Field(..., max_length=200, description="工程名称")
    construction_site: str = Field(..., max_length=200, description="施工部位")
    strength_grade: str = Field(..., max_length=20, description="强度等级")
    planned_volume: float = Field(..., ge=0, description="计划方量")
    actual_volume: Optional[float] = Field(None, ge=0, description="实际方量")
    production_start: Optional[datetime] = Field(None, description="生产开始时间")
    production_end: Optional[datetime] = Field(None, description="生产结束时间")
    truck_no: Optional[str] = Field(None, max_length=50, description="车号")
    driver: Optional[str] = Field(None, max_length=50, description="司机")
    operator: str = Field(..., max_length=50, description="操作员")
    remark: Optional[str] = Field(None, description="备注")
    status: str = Field("待生产", max_length=20, description="状态")


class ProductionBatchCreate(ProductionBatchBase):
    """生产批次创建模型"""
    pass


class ProductionBatchUpdate(BaseModel):
    """生产批次更新模型"""
    project_name: Optional[str] = Field(None, max_length=200, description="工程名称")
    construction_site: Optional[str] = Field(None, max_length=200, description="施工部位")
    strength_grade: Optional[str] = Field(None, max_length=20, description="强度等级")
    planned_volume: Optional[float] = Field(None, ge=0, description="计划方量")
    actual_volume: Optional[float] = Field(None, ge=0, description="实际方量")
    production_start: Optional[datetime] = Field(None, description="生产开始时间")
    production_end: Optional[datetime] = Field(None, description="生产结束时间")
    truck_no: Optional[str] = Field(None, max_length=50, description="车号")
    driver: Optional[str] = Field(None, max_length=50, description="司机")
    operator: Optional[str] = Field(None, max_length=50, description="操作员")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="状态")


class ProductionBatchResponse(ProductionBatchBase):
    """生产批次响应模型"""
    id: int = Field(..., description="生产批次ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
