"""
角色数据模式
定义角色相关的Pydantic模型，用于数据验证和序列�?
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """
    角色基础模型
    包含角色的基本信息字�?
    """
    
    name: str = Field(..., min_length=2, max_length=50, description="角色名称")
    code: str = Field(..., min_length=2, max_length=50, description="角色代码（用于权限检查）")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    is_active: Optional[bool] = Field(default=True, description="是否激�?)


class RoleCreate(RoleBase):
    """
    角色创建模型
    用于创建新角色时的数据验�?
    """
    
    permission_ids: Optional[List[int]] = Field(default=None, description="权限ID列表")


class RoleUpdate(BaseModel):
    """
    角色更新模型
    用于更新角色信息时的数据验证
    所有字段都是可选的
    """
    
    name: Optional[str] = Field(None, min_length=2, max_length=50, description="角色名称")
    code: Optional[str] = Field(None, min_length=2, max_length=50, description="角色代码")
    description: Optional[str] = Field(None, max_length=255, description="角色描述")
    is_active: Optional[bool] = Field(None, description="是否激�?)
    permission_ids: Optional[List[int]] = Field(default=None, description="权限ID列表")


class RoleResponse(RoleBase):
    """
    角色响应模型
    用于返回角色信息给前�?
    """
    
    id: int = Field(..., description="角色ID")
    is_system: bool = Field(default=False, description="是否系统内置角色")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "管理�?,
                "code": "admin",
                "description": "系统管理员，拥有所有权�?,
                "is_active": True,
                "is_system": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class RoleWithPermissions(RoleResponse):
    """
    带权限信息的角色响应模型
    用于返回角色信息及其关联的权�?
    """
    
    permissions: List[dict] = Field(default=[], description="权限列表")
    
    class Config:
        from_attributes = True
