from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CropBase(BaseModel):
    """
    作物档案基础模型
    包含作物信息的公共字段
    """
    
    # 作物名称
    name: str = Field(..., min_length=1, max_length=200, description="作物名称")
    
    # 品种
    variety: str = Field(..., min_length=1, max_length=200, description="品种")
    
    # 生长周期（单位：天）
    growth_cycle: int = Field(..., gt=0, description="生长周期(天)")
    
    # 适宜环境（文本描述，如温度、湿度、光照等）
    suitable_environment: Optional[str] = Field(None, description="适宜环境")
    
    # 病虫害记录（文本描述）
    pest_disease_records: Optional[str] = Field(None, description="病虫害记录")
    
    # 施肥标准（文本描述）
    fertilization_standard: Optional[str] = Field(None, description="施肥标准")
    
    # 播种季节
    planting_season: Optional[str] = Field(None, max_length=100, description="播种季节")
    
    # 收获季节
    harvest_season: Optional[str] = Field(None, max_length=100, description="收获季节")
    
    # 备注信息
    remarks: Optional[str] = Field(None, description="备注信息")


class CropCreate(CropBase):
    """
    创建作物时使用的模型
    继承自CropBase，无需额外字段
    """
    pass


class CropUpdate(BaseModel):
    """
    更新作物时使用的模型
    所有字段都是可选的
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="作物名称")
    variety: Optional[str] = Field(None, min_length=1, max_length=200, description="品种")
    growth_cycle: Optional[int] = Field(None, gt=0, description="生长周期(天)")
    suitable_environment: Optional[str] = Field(None, description="适宜环境")
    pest_disease_records: Optional[str] = Field(None, description="病虫害记录")
    fertilization_standard: Optional[str] = Field(None, description="施肥标准")
    planting_season: Optional[str] = Field(None, max_length=100, description="播种季节")
    harvest_season: Optional[str] = Field(None, max_length=100, description="收获季节")
    remarks: Optional[str] = Field(None, description="备注信息")


class CropResponse(CropBase):
    """
    作物响应模型
    包含从数据库读取时返回的所有字段
    """
    
    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
