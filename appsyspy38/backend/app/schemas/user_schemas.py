"""
用户相关Pydantic模型
用于API请求和响应的数据验证
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色代码")
    description: Optional[str] = Field(None, description="角色描述")


class RoleCreate(RoleBase):
    """创建角色模型"""
    pass


class RoleResponse(RoleBase):
    """角色响应模型"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionBase(BaseModel):
    """权限基础模型"""
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限代码")
    description: Optional[str] = Field(None, description="权限描述")
    module: Optional[str] = Field(None, description="所属模块")


class PermissionCreate(PermissionBase):
    """创建权限模型"""
    pass


class PermissionResponse(PermissionBase):
    """权限响应模型"""
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """用户基础模型"""
    username: Optional[str] = Field(None, description="用户名")
    phone: str = Field(..., description="手机号")
    real_name: Optional[str] = Field(None, description="真实姓名")


class UserCreate(BaseModel):
    """创建用户模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    phone: str = Field(..., description="手机号")
    role_codes: List[str] = Field(default_factory=list, description="角色代码列表")


class UserUpdate(BaseModel):
    """更新用户模型"""
    real_name: Optional[str] = Field(None, description="真实姓名")
    phone: Optional[str] = Field(None, description="手机号")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: Optional[str]
    phone: str
    real_name: Optional[str]
    is_verified: bool
    is_active: bool
    is_first_login: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True


class UserWithPermission(UserResponse):
    """带权限的用户响应模型"""
    permissions: List[str] = []


class LoginRequest(BaseModel):
    """登录请求基础模型"""
    pass


class PasswordLoginRequest(LoginRequest):
    """账号密码登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class PhoneLoginRequest(LoginRequest):
    """手机号验证码登录请求"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., description="验证码")


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号")


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    is_first_login: bool


class RealNameVerifyRequest(BaseModel):
    """实名认证请求"""
    real_name: str = Field(..., description="真实姓名")
    id_card: str = Field(..., description="身份证号")


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")


class ApiResponse(BaseModel):
    """通用API响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    items: List
