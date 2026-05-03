"""
分类Pydantic模型
用于分类相关API的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """
    分类基础模型
    """
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: Optional[int] = Field(0, ge=0, description="排序")


class CategoryCreate(CategoryBase):
    """
    分类创建模型
    """
    pass


class CategoryUpdate(BaseModel):
    """
    分类更新模型
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: Optional[int] = Field(None, ge=0, description="排序")


class CategoryResponse(CategoryBase):
    """
    分类响应模型
    """
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
