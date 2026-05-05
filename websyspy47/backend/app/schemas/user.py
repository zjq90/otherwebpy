from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from .common import validate_phone, validate_password

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, max_length=11, description="手机号")
    email: Optional[EmailStr] = Field(None, max_length=100, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    address: Optional[str] = Field(None, max_length=500, description="地址")
    user_type: Optional[int] = Field(0, description="用户类型：0-普通用户，1-管理员，2-客服")
    status: Optional[int] = Field(1, description="状态：0-禁用，1-正常")

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v, is_new=True)

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    address: Optional[str] = None
    user_type: Optional[int] = None
    status: Optional[int] = None
    password: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return validate_password(v, is_new=False)

class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    points: int = 0
    total_points: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """用户列表响应模型"""
    id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    user_type: int
    status: int
    points: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    """反馈基础模型"""
    user_id: int
    feedback_type: Optional[int] = Field(1, description="反馈类型：0-投诉，1-建议，2-咨询")
    title: str = Field(..., max_length=200, description="标题")
    content: str = Field(..., description="内容")
    contact: Optional[str] = Field(None, max_length=100, description="联系方式")

class FeedbackCreate(FeedbackBase):
    """反馈创建模型"""
    pass

class FeedbackUpdate(BaseModel):
    """反馈更新模型"""
    status: Optional[int] = None
    reply: Optional[str] = None
    reply_user_id: Optional[int] = None

class FeedbackResponse(FeedbackBase):
    """反馈响应模型"""
    id: int
    status: int
    reply: Optional[str] = None
    reply_user_id: Optional[int] = None
    reply_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
