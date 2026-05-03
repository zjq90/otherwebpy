from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    """
    角色管理基础模型
    包含角色信息的公共字段
    """
    
    # 角色名称
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    
    # 角色代码
    code: str = Field(..., min_length=1, max_length=100, description="角色代码")
    
    # 角色描述
    description: Optional[str] = Field(None, max_length=500, description="角色描述")
    
    # 权限列表（逗号分隔的字符串或列表）
    permissions: Optional[str] = Field(None, description="权限列表")
    
    # 是否为默认角色
    is_default: bool = Field(default=False, description="是否默认角色")
    
    # 排序顺序
    sort_order: int = Field(default=0, description="排序顺序")


class RoleCreate(RoleBase):
    """
    创建角色时使用的模型
    """
    pass


class RoleUpdate(BaseModel):
    """
    更新角色时使用的模型
    所有字段都是可选的
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, max_length=500, description="角色描述")
    permissions: Optional[str] = Field(None, description="权限列表")
    is_default: Optional[bool] = Field(None, description="是否默认角色")
    sort_order: Optional[int] = Field(None, description="排序顺序")


class RoleResponse(RoleBase):
    """
    角色响应模型
    包含从数据库读取时返回的所有字段
    """
    
    id: int = Field(..., description="主键ID")
    is_system: bool = Field(..., description="是否系统预设")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    # 权限列表（解析后的数组格式）
    permission_list: Optional[List[str]] = Field(None, description="权限列表（数组格式）")
    
    class Config:
        from_attributes = True
