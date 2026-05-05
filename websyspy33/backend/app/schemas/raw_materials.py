# -*- coding: utf-8 -*-
"""
原材料数据模型
==============
定义原材料相关的Pydantic数据模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RawMaterialBase(BaseModel):
    """原材料基础模型"""
    name: str = Field(..., max_length=100, description="原材料名称")
    code: str = Field(..., max_length=50, description="原材料编码")
    material_type: str = Field(..., max_length=50, description="材料类型")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    description: Optional[str] = Field(None, description="描述")
    status: bool = Field(True, description="状态")


class RawMaterialCreate(RawMaterialBase):
    """原材料创建模型"""
    pass


class RawMaterialUpdate(BaseModel):
    """原材料更新模型"""
    name: Optional[str] = Field(None, max_length=100, description="原材料名称")
    material_type: Optional[str] = Field(None, max_length=50, description="材料类型")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: Optional[str] = Field(None, max_length=20, description="计量单位")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    description: Optional[str] = Field(None, description="描述")
    status: Optional[bool] = Field(None, description="状态")


class RawMaterialResponse(RawMaterialBase):
    """原材料响应模型"""
    id: int = Field(..., description="原材料ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
