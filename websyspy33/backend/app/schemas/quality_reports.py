# -*- coding: utf-8 -*-
"""
质量报告数据模型
================
定义质量报告相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class QualityReportBase(BaseModel):
    """质量报告基础模型"""
    report_no: str = Field(..., max_length=50, description="报告编号")
    batch_id: int = Field(..., description="生产批次ID")
    report_type: str = Field(..., max_length=50, description="报告类型")
    report_date: date = Field(..., description="报告日期")
    generated_by: str = Field(..., max_length=50, description="生成人")
    material_inspection_ids: Optional[str] = Field(None, description="关联原材料检验ID")
    production_record_ids: Optional[str] = Field(None, description="关联生产记录ID")
    strength_test_ids: Optional[str] = Field(None, description="关联强度试验ID")
    summary: Optional[str] = Field(None, description="报告摘要")
    conclusion: Optional[str] = Field(None, description="报告结论")
    overall_result: str = Field("待评定", max_length=20, description="综合评定结果")
    is_qualified: bool = Field(False, description="是否合格")
    remark: Optional[str] = Field(None, description="备注")
    status: str = Field("草稿", max_length=20, description="状态")
    approved_by: Optional[str] = Field(None, max_length=50, description="批准人")
    approval_date: Optional[date] = Field(None, description="批准日期")


class QualityReportCreate(QualityReportBase):
    """质量报告创建模型"""
    pass


class QualityReportUpdate(BaseModel):
    """质量报告更新模型"""
    report_type: Optional[str] = Field(None, max_length=50, description="报告类型")
    report_date: Optional[date] = Field(None, description="报告日期")
    generated_by: Optional[str] = Field(None, max_length=50, description="生成人")
    material_inspection_ids: Optional[str] = Field(None, description="关联原材料检验ID")
    production_record_ids: Optional[str] = Field(None, description="关联生产记录ID")
    strength_test_ids: Optional[str] = Field(None, description="关联强度试验ID")
    summary: Optional[str] = Field(None, description="报告摘要")
    conclusion: Optional[str] = Field(None, description="报告结论")
    overall_result: Optional[str] = Field(None, max_length=20, description="综合评定结果")
    is_qualified: Optional[bool] = Field(None, description="是否合格")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    approved_by: Optional[str] = Field(None, max_length=50, description="批准人")
    approval_date: Optional[date] = Field(None, description="批准日期")


class QualityReportResponse(QualityReportBase):
    """质量报告响应模型"""
    id: int = Field(..., description="质量报告ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
