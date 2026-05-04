"""
用户数据验证模块
定义用户相关的请求和响应数据结构
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


class UserCreate(UserBase):
    """用户创建模型（注册用）"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class WechatLogin(BaseModel):
    """微信登录模型"""
    code: str = Field(..., description="微信登录授权码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    avatar: Optional[str] = Field(None, max_length=500, description="头像URL")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    avatar: Optional[str] = Field(None, description="头像URL")
    wechat_openid: Optional[str] = Field(None, description="微信OpenID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    class Config:
        """Pydantic配置"""
        from_attributes = True


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


class TokenPayload(BaseModel):
    """令牌载荷模型"""
    sub: Optional[int] = Field(None, description="用户ID")
    exp: Optional[datetime] = Field(None, description="过期时间")
