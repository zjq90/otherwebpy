"""
用户数据验证模型
定义用户相关的请求和响应数据结构
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    """
    用户基础模型
    包含用户的基本信息字段
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    phone: str = Field(..., min_length=11, max_length=20, description="手机号码")
    role: UserRole = Field(default=UserRole.DRIVER, description="用户角色")

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """
    用户创建模型
    用于创建新用户时的数据验证
    """
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    driver_license: Optional[str] = Field(default=None, max_length=50, description="驾驶证号（司机角色必填）")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        验证密码强度
        """
        if len(v) < 6:
            raise ValueError('密码长度不能少于6位')
        return v


class UserUpdate(BaseModel):
    """
    用户更新模型
    用于更新用户信息时的数据验证
    """
    real_name: Optional[str] = Field(default=None, min_length=2, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(default=None, min_length=11, max_length=20, description="手机号码")
    password: Optional[str] = Field(default=None, min_length=6, max_length=100, description="新密码")
    status: Optional[UserStatus] = Field(default=None, description="用户状态")
    driver_license: Optional[str] = Field(default=None, max_length=50, description="驾驶证号")
    vehicle_id: Optional[int] = Field(default=None, description="关联车辆ID")

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    用户响应模型
    用于返回用户信息（不包含密码等敏感信息）
    """
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    real_name: str = Field(description="真实姓名")
    phone: str = Field(description="手机号码")
    role: UserRole = Field(description="用户角色")
    status: UserStatus = Field(description="用户状态")
    driver_license: Optional[str] = Field(default=None, description="驾驶证号")
    vehicle_id: Optional[int] = Field(default=None, description="关联车辆ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    last_login_at: Optional[datetime] = Field(default=None, description="最后登录时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "real_name": "管理员",
                "phone": "13800138000",
                "role": "admin",
                "status": "active",
                "driver_license": None,
                "vehicle_id": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "last_login_at": "2024-01-01T00:00:00"
            }
        }


class UserLogin(BaseModel):
    """
    用户登录模型
    用于用户登录时的数据验证
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "123456"
            }
        }


class UserLoginResponse(BaseModel):
    """
    用户登录响应模型
    用于登录成功后返回用户信息和令牌
    """
    user: UserResponse = Field(description="用户信息")
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(description="令牌有效期（秒）")

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """
    用户列表响应模型
    用于返回用户列表数据
    """
    items: list[UserResponse] = Field(description="用户列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")

    class Config:
        from_attributes = True


class DriverSimpleResponse(BaseModel):
    """
    司机简易响应模型
    用于任务分配时显示司机列表
    """
    id: int = Field(description="用户ID")
    real_name: str = Field(description="真实姓名")
    phone: str = Field(description="手机号码")
    status: UserStatus = Field(description="用户状态")
    vehicle_id: Optional[int] = Field(default=None, description="关联车辆ID")

    class Config:
        from_attributes = True
