"""
权限数据模式
定义权限相关的Pydantic模型，用于数据验证和序列�?
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """
    权限基础模型
    包含权限的基本信息字�?
    """
    
    name: str = Field(..., min_length=2, max_length=100, description="权限名称")
    code: str = Field(..., min_length=2, max_length=100, description="权限代码（用于权限检查）")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")
    module: Optional[str] = Field(None, max_length=50, description="所属模�?)
    action: Optional[str] = Field(None, max_length=50, description="操作类型")
    is_active: Optional[bool] = Field(default=True, description="是否激�?)


class PermissionCreate(PermissionBase):
    """
    权限创建模型
    用于创建新权限时的数据验�?
    """
    
    pass


class PermissionUpdate(BaseModel):
    """
    权限更新模型
    用于更新权限信息时的数据验证
    所有字段都是可选的
    """
    
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="权限名称")
    code: Optional[str] = Field(None, min_length=2, max_length=100, description="权限代码")
    description: Optional[str] = Field(None, max_length=255, description="权限描述")
    module: Optional[str] = Field(None, max_length=50, description="所属模�?)
    action: Optional[str] = Field(None, max_length=50, description="操作类型")
    is_active: Optional[bool] = Field(None, description="是否激�?)


class PermissionResponse(PermissionBase):
    """
    权限响应模型
    用于返回权限信息给前�?
    """
    
    id: int = Field(..., description="权限ID")
    is_system: bool = Field(default=False, description="是否系统内置权限")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "用户列表查询",
                "code": "user:read",
                "description": "查看用户列表的权�?,
                "module": "user",
                "action": "read",
                "is_active": True,
                "is_system": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
