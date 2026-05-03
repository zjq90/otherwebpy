"""
用户Pydantic模型
用于用户相关API的请求和响应数据验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    用户基础模型
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    name: Optional[str] = Field(None, max_length=50, description="姓名")


class UserCreate(UserBase):
    """
    用户创建模型
    用于注册请求
    """
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    """
    用户登录模型
    """
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    name: Optional[str] = Field(None, max_length=50, description="姓名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="密码")


class UserResponse(UserBase):
    """
    用户响应模型
    用于API返回用户信息
    """
    id: int
    role: str
    is_verified: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
