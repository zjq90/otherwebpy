# -*- coding: utf-8 -*-
"""
原材料检验数据模型
==================
定义原材料检验相关的Pydantic数据模型
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class MaterialInspectionBase(BaseModel):
    """原材料检验基础模型"""
    inspection_no: str = Field(..., max_length=50, description="检验单号")
    material_id: int = Field(..., description="原材料ID")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    batch_no: str = Field(..., max_length=50, description="进场批次号")
    sample_no: str = Field(..., max_length=50, description="样品编号")
    sample_date: date = Field(..., description="取样日期")
    inspector: str = Field(..., max_length=50, description="检验员")
    inspection_date: date = Field(..., description="检验日期")
    inspection_items: Optional[str] = Field(None, description="检验项目(JSON格式)")
    test_data: Optional[str] = Field(None, description="检测数据(JSON格式)")
    standard_value: Optional[str] = Field(None, description="标准值(JSON格式)")
    result: str = Field("待检", max_length=20, description="检验结果")
    conclusion: Optional[str] = Field(None, description="检验结论")
    is_qualified: bool = Field(False, description="是否合格")
    lab_temperature: Optional[float] = Field(None, description="实验室温度")
    lab_humidity: Optional[float] = Field(None, description="实验室湿度")
    remark: Optional[str] = Field(None, description="备注")
    status: str = Field("草稿", max_length=20, description="状态")
    reviewed_by: Optional[str] = Field(None, max_length=50, description="审核人")
    review_date: Optional[date] = Field(None, description="审核日期")


class MaterialInspectionCreate(MaterialInspectionBase):
    """原材料检验创建模型"""
    pass


class MaterialInspectionUpdate(BaseModel):
    """原材料检验更新模型"""
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    batch_no: Optional[str] = Field(None, max_length=50, description="进场批次号")
    sample_no: Optional[str] = Field(None, max_length=50, description="样品编号")
    sample_date: Optional[date] = Field(None, description="取样日期")
    inspector: Optional[str] = Field(None, max_length=50, description="检验员")
    inspection_date: Optional[date] = Field(None, description="检验日期")
    inspection_items: Optional[str] = Field(None, description="检验项目(JSON格式)")
    test_data: Optional[str] = Field(None, description="检测数据(JSON格式)")
    standard_value: Optional[str] = Field(None, description="标准值(JSON格式)")
    result: Optional[str] = Field(None, max_length=20, description="检验结果")
    conclusion: Optional[str] = Field(None, description="检验结论")
    is_qualified: Optional[bool] = Field(None, description="是否合格")
    lab_temperature: Optional[float] = Field(None, description="实验室温度")
    lab_humidity: Optional[float] = Field(None, description="实验室湿度")
    remark: Optional[str] = Field(None, description="备注")
    status: Optional[str] = Field(None, max_length=20, description="状态")
    reviewed_by: Optional[str] = Field(None, max_length=50, description="审核人")
    review_date: Optional[date] = Field(None, description="审核日期")


class MaterialInspectionResponse(MaterialInspectionBase):
    """原材料检验响应模型"""
    id: int = Field(..., description="检验记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
