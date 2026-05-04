from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    """
    用户基础模型
    包含用户的基本信息字段
    """
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="电子邮箱")
    room_number: Optional[str] = Field(None, max_length=20, description="房间号")
    role: str = Field(default=UserRole.RESIDENT.value, description="用户角色")


class UserCreate(UserBase):
    """
    用户创建模型
    用于创建新用户时的请求体
    """
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """
    用户更新模型
    用于更新用户信息时的请求体
    """
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="电子邮箱")
    room_number: Optional[str] = Field(None, max_length=20, description="房间号")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserResponse(UserBase):
    """
    用户响应模型
    用于返回用户信息时的响应体
    """
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    用户登录模型
    用于用户登录时的请求体
    """
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class Token(BaseModel):
    """
    令牌响应模型
    用于登录成功后返回的令牌信息
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")
