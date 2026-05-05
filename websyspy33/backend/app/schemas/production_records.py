# -*- coding: utf-8 -*-
"""
生产记录数据模型
================
定义生产记录相关的Pydantic数据模型
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProductionRecordBase(BaseModel):
    """生产记录基础模型"""
    batch_id: int = Field(..., description="生产批次ID")
    record_no: str = Field(..., max_length=50, description="记录编号")
    mix_no: int = Field(..., ge=1, description="盘数序号")
    mixing_time: float = Field(..., ge=0, description="搅拌时间(秒)")
    feeding_sequence: Optional[str] = Field(None, description="投料顺序(JSON格式)")
    actual_cement: float = Field(..., ge=0, description="实际水泥用量")
    actual_sand: float = Field(..., ge=0, description="实际砂用量")
    actual_stone: float = Field(..., ge=0, description="实际石用量")
    actual_water: float = Field(..., ge=0, description="实际水用量")
    actual_admixture: Optional[float] = Field(None, ge=0, description="实际外加剂用量")
    actual_fly_ash: Optional[float] = Field(None, ge=0, description="实际粉煤灰用量")
    actual_water_cement_ratio: float = Field(..., ge=0, le=1, description="实际水胶比")
    design_water_cement_ratio: float = Field(..., ge=0, le=1, description="设计水胶比")
    deviation_rate: float = Field(..., ge=-100, le=100, description="偏差率(%)")
    slump_actual: Optional[float] = Field(None, ge=0, description="实际坍落度")
    temperature: Optional[float] = Field(None, description="出机温度")
    is_normal: bool = Field(True, description="是否正常")
    anomaly_reason: Optional[str] = Field(None, description="异常原因")
    operator: str = Field(..., max_length=50, description="操作员")
    record_time: datetime = Field(default_factory=datetime.now, description="记录时间")
    remark: Optional[str] = Field(None, description="备注")


class ProductionRecordCreate(ProductionRecordBase):
    """生产记录创建模型"""
    pass


class ProductionRecordUpdate(BaseModel):
    """生产记录更新模型"""
    mixing_time: Optional[float] = Field(None, ge=0, description="搅拌时间(秒)")
    feeding_sequence: Optional[str] = Field(None, description="投料顺序(JSON格式)")
    actual_cement: Optional[float] = Field(None, ge=0, description="实际水泥用量")
    actual_sand: Optional[float] = Field(None, ge=0, description="实际砂用量")
    actual_stone: Optional[float] = Field(None, ge=0, description="实际石用量")
    actual_water: Optional[float] = Field(None, ge=0, description="实际水用量")
    actual_admixture: Optional[float] = Field(None, ge=0, description="实际外加剂用量")
    actual_fly_ash: Optional[float] = Field(None, ge=0, description="实际粉煤灰用量")
    actual_water_cement_ratio: Optional[float] = Field(None, ge=0, le=1, description="实际水胶比")
    design_water_cement_ratio: Optional[float] = Field(None, ge=0, le=1, description="设计水胶比")
    deviation_rate: Optional[float] = Field(None, ge=-100, le=100, description="偏差率(%)")
    slump_actual: Optional[float] = Field(None, ge=0, description="实际坍落度")
    temperature: Optional[float] = Field(None, description="出机温度")
    is_normal: Optional[bool] = Field(None, description="是否正常")
    anomaly_reason: Optional[str] = Field(None, description="异常原因")
    operator: Optional[str] = Field(None, max_length=50, description="操作员")
    record_time: Optional[datetime] = Field(None, description="记录时间")
    remark: Optional[str] = Field(None, description="备注")


class ProductionRecordResponse(ProductionRecordBase):
    """生产记录响应模型"""
    id: int = Field(..., description="生产记录ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
