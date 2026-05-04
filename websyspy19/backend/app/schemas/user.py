"""
用户数据模式
定义用户相关的Pydantic模型，用于数据验证和序列�?
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """
    用户基础模型
    包含用户的基本信息字�?
    """
    
    username: str = Field(..., min_length=3, max_length=50, description="用户�?)
    email: Optional[EmailStr] = Field(None, max_length=100, description="邮箱地址")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机�?)
    full_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    is_active: Optional[bool] = Field(default=True, description="是否激�?)


class UserCreate(UserBase):
    """
    用户创建模型
    用于创建新用户时的数据验�?
    """
    
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    role_ids: Optional[List[int]] = Field(default=None, description="角色ID列表")


class UserUpdate(BaseModel):
    """
    用户更新模型
    用于更新用户信息时的数据验证
    所有字段都是可选的
    """
    
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户�?)
    email: Optional[EmailStr] = Field(None, max_length=100, description="邮箱地址")
    phone: Optional[str] = Field(None, min_length=11, max_length=20, description="手机�?)
    full_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    is_active: Optional[bool] = Field(None, description="是否激�?)
    password: Optional[str] = Field(None, min_length=6, max_length=50, description="密码")
    role_ids: Optional[List[int]] = Field(default=None, description="角色ID列表")


class UserLogin(BaseModel):
    """
    用户登录模型
    用于用户登录时的数据验证
    """
    
    username: str = Field(..., min_length=3, max_length=50, description="用户�?)
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserResponse(UserBase):
    """
    用户响应模型
    用于返回用户信息给前�?
    不包含密码等敏感信息
    """
    
    id: int = Field(..., description="用户ID")
    is_superuser: bool = Field(default=False, description="是否超级管理�?)
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时�?)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "phone": "13800138000",
                "full_name": "管理�?,
                "is_active": True,
                "is_superuser": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "last_login": "2024-01-01T00:00:00"
            }
        }


class UserWithRoles(UserResponse):
    """
    带角色信息的用户响应模型
    用于返回用户信息及其关联的角�?
    """
    
    roles: List[dict] = Field(default=[], description="角色列表")
    
    class Config:
        from_attributes = True
