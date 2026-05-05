# -*- coding: utf-8 -*-
"""
供应商评级数据模型
==================
定义供应商评级相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupplierRatingBase(BaseModel):
    """供应商评级基础模型"""
    rating_no: str = Field(..., max_length=50, description="评级编号")
    supplier_id: int = Field(..., description="供应商ID")
    rating_period: str = Field(..., max_length=50, description="评级周期")
    rating_date: date = Field(..., description="评级日期")
    quality_score: float = Field(..., ge=0, le=40, description="材料质量评分")
    delivery_score: float = Field(..., ge=0, le=30, description="供货及时性评分")
    price_score: float = Field(..., ge=0, le=20, description="价格合理性评分")
    service_score: float = Field(..., ge=0, le=10, description="售后服务评分")
    total_score: float = Field(..., ge=0, le=100, description="综合评分")
    rating_level: str = Field(..., max_length=20, description="评级等级")
    inspection_count: int = Field(0, ge=0, description="检验批次数量")
    pass_rate: float = Field(100.0, ge=0, le=100, description="合格率")
    delivery_count: int = Field(0, ge=0, description="供货次数")
    on_time_rate: float = Field(100.0, ge=0, le=100, description="准时率")
    remark: Optional[str] = Field(None, description="评级说明")
    rater: str = Field(..., max_length=50, description="评级人")
    status: str = Field("草稿", max_length=20, description="状态")


class SupplierRatingCreate(SupplierRatingBase):
    """供应商评级创建模型"""
    pass


class SupplierRatingUpdate(BaseModel):
    """供应商评级更新模型"""
    rating_period: Optional[str] = Field(None, max_length=50, description="评级周期")
    rating_date: Optional[date] = Field(None, description="评级日期")
    quality_score: Optional[float] = Field(None, ge=0, le=40, description="材料质量评分")
    delivery_score: Optional[float] = Field(None, ge=0, le=30, description="供货及时性评分")
    price_score: Optional[float] = Field(None, ge=0, le=20, description="价格合理性评分")
    service_score: Optional[float] = Field(None, ge=0, le=10, description="售后服务评分")
    total_score: Optional[float] = Field(None, ge=0, le=100, description="综合评分")
    rating_level: Optional[str] = Field(None, max_length=20, description="评级等级")
    inspection_count: Optional[int] = Field(None, ge=0, description="检验批次数量")
    pass_rate: Optional[float] = Field(None, ge=0, le=100, description="合格率")
    delivery_count: Optional[int] = Field(None, ge=0, description="供货次数")
    on_time_rate: Optional[float] = Field(None, ge=0, le=100, description="准时率")
    remark: Optional[str] = Field(None, description="评级说明")
    rater: Optional[str] = Field(None, max_length=50, description="评级人")
    status: Optional[str] = Field(None, max_length=20, description="状态")


class SupplierRatingResponse(SupplierRatingBase):
    """供应商评级响应模型"""
    id: int = Field(..., description="评级记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
