from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PlotBase(BaseModel):
    """
    地块管理基础模型
    包含地块信息的公共字段
    """
    
    # 地块编号
    plot_number: str = Field(..., min_length=1, max_length=50, description="地块编号")
    
    # 关联的农场ID
    farm_id: int = Field(..., gt=0, description="所属农场ID")
    
    # 地块面积（单位：亩）
    area: float = Field(..., gt=0, description="地块面积(亩)")
    
    # 土壤类型
    soil_type: str = Field(..., min_length=1, max_length=100, description="土壤类型")
    
    # pH值
    ph_value: float = Field(..., ge=0, le=14, description="土壤pH值")
    
    # 种植历史（文本描述）
    planting_history: Optional[str] = Field(None, description="种植历史")
    
    # 轮作计划（文本描述）
    crop_rotation_plan: Optional[str] = Field(None, description="轮作计划")
    
    # 是否禁用农药（是/否）
    pesticide_prohibited: bool = Field(default=False, description="是否禁用农药")
    
    # 地块位置描述
    location: Optional[str] = Field(None, max_length=500, description="地块位置描述")
    
    # 备注信息
    remarks: Optional[str] = Field(None, description="备注信息")


class PlotCreate(PlotBase):
    """
    创建地块时使用的模型
    继承自PlotBase，无需额外字段
    """
    pass


class PlotUpdate(BaseModel):
    """
    更新地块时使用的模型
    所有字段都是可选的
    """
    
    plot_number: Optional[str] = Field(None, min_length=1, max_length=50, description="地块编号")
    farm_id: Optional[int] = Field(None, gt=0, description="所属农场ID")
    area: Optional[float] = Field(None, gt=0, description="地块面积(亩)")
    soil_type: Optional[str] = Field(None, min_length=1, max_length=100, description="土壤类型")
    ph_value: Optional[float] = Field(None, ge=0, le=14, description="土壤pH值")
    planting_history: Optional[str] = Field(None, description="种植历史")
    crop_rotation_plan: Optional[str] = Field(None, description="轮作计划")
    pesticide_prohibited: Optional[bool] = Field(None, description="是否禁用农药")
    location: Optional[str] = Field(None, max_length=500, description="地块位置描述")
    remarks: Optional[str] = Field(None, description="备注信息")


class PlotResponse(PlotBase):
    """
    地块响应模型
    包含从数据库读取时返回的所有字段
    """
    
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
