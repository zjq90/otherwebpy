# -*- coding: utf-8 -*-
"""
配比设计数据模型
================
定义配比设计相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class MixDesignBase(BaseModel):
    """配比设计基础模型"""
    design_no: str = Field(..., max_length=50, description="设计编号")
    mix_name: str = Field(..., max_length=100, description="配合比名称")
    strength_grade: str = Field(..., max_length=20, description="强度等级")
    design_age: int = Field(28, ge=1, description="设计龄期")
    slump: Optional[float] = Field(None, ge=0, description="坍落度要求")
    cement_content: float = Field(..., ge=0, description="水泥用量")
    sand_content: float = Field(..., ge=0, description="砂用量")
    stone_content: float = Field(..., ge=0, description="石用量")
    water_content: float = Field(..., ge=0, description="水用量")
    admixture_content: Optional[float] = Field(None, ge=0, description="外加剂用量")
    fly_ash_content: Optional[float] = Field(None, ge=0, description="粉煤灰用量")
    water_cement_ratio: float = Field(..., ge=0, le=1, description="水胶比")
    sand_ratio: float = Field(..., ge=0, le=100, description="砂率")
    designed_by: str = Field(..., max_length=50, description="设计人")
    design_date: date = Field(..., description="设计日期")
    approved_by: Optional[str] = Field(None, max_length=50, description="批准人")
    approval_date: Optional[date] = Field(None, description="批准日期")
    remark: Optional[str] = Field(None, description="备注")
    status: str = Field("草稿", max_length=20, description="状态")
    is_active: bool = Field(False, description="是否启用")


class MixDesignCreate(MixDesignBase):
    """配比设计创建模型"""
    pass


class MixDesignUpdate(BaseModel):
    """配比设计更新模型"""
    mix_name: Optional[str] = Field(None, max_length=100, description="配合比名称")
    strength_grade: Optional[str] = Field(None, max_length=20, description="强度等级")
    design_age: Optional[int] = Field(None, ge=1, description="设计龄期")
    slump: Optional[float] = Field(None, ge=0, description="坍落度要求")
    cement_content: Optional[float] = Field(None, ge=0, description="水泥用量")
    sand_content: Optional[float] = Field(None, ge=0, description="砂用量")
    stone_content: Optional[float] = Field(None, ge=0, description="石用量")
    water_content: Optional[float] = Field(None, ge=0, description="水用量")
    admixture_content: Optional[float] = Field(None, ge=0, description="外加剂用量")
    fly_ash_content: Optional[float] = Field(None, ge=0, description="粉煤灰用量")
    water_cement_ratio: Optional[float] = Field(None, ge=0, le=1, description="水胶比")
    sand_ratio: Optional[float] = Field(None, ge=0, le=100, description="砂率")
    designed_by: Optional[str] = Field(None, max_length=50, description="设计人")
    design_date: Optional[date] = Field(None, description="设计日期")
    approved_by: Optional[str] = Field(None, max_length=50, description="批准人")
    approval_date: Optional[date] = Field(None, description="批准日期")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    is_active: Optional[bool] = Field(None, description="是否启用")


class MixDesignResponse(MixDesignBase):
    """配比设计响应模型"""
    id: int = Field(..., description="配比设计ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
