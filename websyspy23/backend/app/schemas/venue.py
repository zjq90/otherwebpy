"""
场地管理Pydantic Schema
定义场地的请求/响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VenueBase(BaseModel):
    """
    场地基础Schema
    包含场地的基本字段
    """
    name: str = Field(..., min_length=1, max_length=100, description="场地名称")
    code: str = Field(..., min_length=1, max_length=50, description="场地代码")
    venue_type: str = Field(..., min_length=1, max_length=50, description="场地类型")
    capacity: int = Field(20, gt=0, description="场地容量")
    location: Optional[str] = Field(None, max_length=200, description="场地位置")
    facilities: Optional[str] = Field(None, description="场地设施")
    description: Optional[str] = Field(None, description="场地描述")
    is_active: Optional[bool] = Field(True, description="是否启用")
    sort_order: Optional[int] = Field(0, description="排序权重")


class VenueCreate(VenueBase):
    """
    场地创建Schema
    继承自VenueBase，用于创建新的场地
    """
    pass


class VenueUpdate(BaseModel):
    """
    场地更新Schema
    所有字段都是可选的，用于部分更新
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="场地名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="场地代码")
    venue_type: Optional[str] = Field(None, min_length=1, max_length=50, description="场地类型")
    capacity: Optional[int] = Field(None, gt=0, description="场地容量")
    location: Optional[str] = Field(None, max_length=200, description="场地位置")
    facilities: Optional[str] = Field(None, description="场地设施")
    description: Optional[str] = Field(None, description="场地描述")
    is_active: Optional[bool] = Field(None, description="是否启用")
    sort_order: Optional[int] = Field(None, description="排序权重")


class VenueResponse(VenueBase):
    """
    场地响应Schema
    包含场地的所有字段，用于返回给前端
    """
    id: int = Field(..., description="场地ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
