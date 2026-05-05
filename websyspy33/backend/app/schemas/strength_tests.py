# -*- coding: utf-8 -*-
"""
强度检测数据模型
================
定义强度检测相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class StrengthTestBase(BaseModel):
    """强度检测基础模型"""
    test_no: str = Field(..., max_length=50, description="试验编号")
    block_id: int = Field(..., description="试块ID")
    test_date: date = Field(..., description="试验日期")
    actual_age: int = Field(..., ge=1, description="实际龄期(天)")
    tester: str = Field(..., max_length=50, description="试验人")
    lab_temperature: Optional[float] = Field(None, description="实验室温度")
    lab_humidity: Optional[float] = Field(None, description="实验室湿度")
    load_1: float = Field(..., ge=0, description="试块1破坏荷载")
    load_2: float = Field(..., ge=0, description="试块2破坏荷载")
    load_3: Optional[float] = Field(None, ge=0, description="试块3破坏荷载")
    strength_1: float = Field(..., ge=0, description="试块1强度")
    strength_2: float = Field(..., ge=0, description="试块2强度")
    strength_3: Optional[float] = Field(None, ge=0, description="试块3强度")
    avg_strength: float = Field(..., ge=0, description="平均强度")
    strength_deviation: Optional[float] = Field(None, description="强度偏差")
    design_strength: float = Field(..., ge=0, description="设计强度值")
    strength_ratio: float = Field(..., ge=0, description="强度比(%)")
    result: str = Field("待评定", max_length=20, description="结果")
    is_qualified: bool = Field(False, description="是否合格")
    conclusion: Optional[str] = Field(None, description="试验结论")
    remark: Optional[str] = Field(None, description="备注")
    status: str = Field("草稿", max_length=20, description="状态")
    reviewed_by: Optional[str] = Field(None, max_length=50, description="审核人")
    review_date: Optional[date] = Field(None, description="审核日期")


class StrengthTestCreate(StrengthTestBase):
    """强度检测创建模型"""
    pass


class StrengthTestUpdate(BaseModel):
    """强度检测更新模型"""
    test_date: Optional[date] = Field(None, description="试验日期")
    actual_age: Optional[int] = Field(None, ge=1, description="实际龄期(天)")
    tester: Optional[str] = Field(None, max_length=50, description="试验人")
    lab_temperature: Optional[float] = Field(None, description="实验室温度")
    lab_humidity: Optional[float] = Field(None, description="实验室湿度")
    load_1: Optional[float] = Field(None, ge=0, description="试块1破坏荷载")
    load_2: Optional[float] = Field(None, ge=0, description="试块2破坏荷载")
    load_3: Optional[float] = Field(None, ge=0, description="试块3破坏荷载")
    strength_1: Optional[float] = Field(None, ge=0, description="试块1强度")
    strength_2: Optional[float] = Field(None, ge=0, description="试块2强度")
    strength_3: Optional[float] = Field(None, ge=0, description="试块3强度")
    avg_strength: Optional[float] = Field(None, ge=0, description="平均强度")
    strength_deviation: Optional[float] = Field(None, description="强度偏差")
    design_strength: Optional[float] = Field(None, ge=0, description="设计强度值")
    strength_ratio: Optional[float] = Field(None, ge=0, description="强度比(%)")
    result: Optional[str] = Field(None, max_length=20, description="结果")
    is_qualified: Optional[bool] = Field(None, description="是否合格")
    conclusion: Optional[str] = Field(None, description="试验结论")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    reviewed_by: Optional[str] = Field(None, max_length=50, description="审核人")
    review_date: Optional[date] = Field(None, description="审核日期")


class StrengthTestResponse(StrengthTestBase):
    """强度检测响应模型"""
    id: int = Field(..., description="强度检测ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
