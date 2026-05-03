"""
Pydantic模型定义
用于API请求和响应的数据验证和序列化
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re


USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{2,50}$')
PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 100


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名（字母、数字、下划线）")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号（11位中国大陆手机号）")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    role: str = Field(default="renter", description="角色：admin/staff/renter")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """验证用户名格式：只能包含字母、数字和下划线"""
        if not USERNAME_PATTERN.match(v):
            raise ValueError('用户名只能包含字母、数字和下划线，长度2-50位')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """验证手机号格式：11位中国大陆手机号"""
        if not PHONE_PATTERN.match(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号（以13-19开头）')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """验证邮箱格式"""
        if v is None or v.strip() == '':
            return None
        v = v.strip()
        if not EMAIL_PATTERN.match(v):
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """验证角色"""
        valid_roles = ['admin', 'staff', 'renter']
        if v not in valid_roles:
            raise ValueError(f'角色必须是以下之一：{valid_roles}')
        return v


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH, description="密码")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f'密码长度至少需要{PASSWORD_MIN_LENGTH}位')
        
        if len(v) > PASSWORD_MAX_LENGTH:
            raise ValueError(f'密码长度不能超过{PASSWORD_MAX_LENGTH}位')
        
        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        
        if not (has_letter and has_digit):
            raise ValueError('密码需要同时包含字母和数字')
        
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, min_length=11, max_length=11, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    status: Optional[str] = Field(None, description="状态：active/inactive")

    @field_validator('phone')
    @classmethod
    def validate_update_phone(cls, v: Optional[str]) -> Optional[str]:
        """验证手机号格式"""
        if v is None:
            return None
        if not PHONE_PATTERN.match(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号（以13-19开头）')
        return v

    @field_validator('email')
    @classmethod
    def validate_update_email(cls, v: Optional[str]) -> Optional[str]:
        """验证邮箱格式"""
        if v is None or v.strip() == '':
            return None
        v = v.strip()
        if not EMAIL_PATTERN.match(v):
            raise ValueError('邮箱格式不正确')
        return v

    @field_validator('status')
    @classmethod
    def validate_update_status(cls, v: Optional[str]) -> Optional[str]:
        """验证状态"""
        if v is None:
            return None
        valid_statuses = ['active', 'inactive']
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一：{valid_statuses}')
        return v


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    balance: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class ItemBase(BaseModel):
    """物品基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="物品名称")
    description: Optional[str] = Field(None, description="物品描述")
    category: Optional[str] = Field(None, max_length=50, description="物品分类")
    daily_rent: float = Field(..., gt=0, description="日租金")
    deposit: float = Field(..., ge=0, description="押金")
    stock: int = Field(default=1, ge=1, description="库存数量")
    image_url: Optional[str] = Field(None, description="物品图片URL")


class ItemCreate(ItemBase):
    """物品创建模型"""
    pass


class ItemUpdate(BaseModel):
    """物品更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    daily_rent: Optional[float] = None
    deposit: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    image_url: Optional[str] = None


class ItemResponse(ItemBase):
    """物品响应模型"""
    id: int
    available: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RentalBase(BaseModel):
    """租借记录基础模型"""
    item_id: int = Field(..., description="物品ID")
    quantity: int = Field(default=1, ge=1, description="租借数量")
    start_date: date = Field(..., description="租借开始日期")
    due_date: date = Field(..., description="应归还日期")
    remark: Optional[str] = Field(None, description="备注")


class RentalCreate(RentalBase):
    """租借记录创建模型"""
    user_id: int = Field(..., description="租借人ID")


class RentalUpdate(BaseModel):
    """租借记录更新模型"""
    actual_return_date: Optional[date] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class RentalResponse(BaseModel):
    """租借记录响应模型"""
    id: int
    rental_no: str
    user_id: int
    item_id: int
    quantity: int
    start_date: date
    due_date: date
    actual_return_date: Optional[date]
    daily_rent: float
    deposit_amount: float
    total_rent: float
    deposit_status: str
    status: str
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RentalDetailResponse(RentalResponse):
    """租借记录详情响应模型（包含关联信息）"""
    renter: Optional[UserResponse] = None
    item: Optional[ItemResponse] = None


class ReminderResponse(BaseModel):
    """提醒记录响应模型"""
    id: int
    rental_id: int
    user_id: int
    reminder_type: str
    reminder_level: str
    title: str
    content: str
    is_read: bool
    is_sent: bool
    sent_at: Optional[datetime]
    reminder_day: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class CollectionOrderResponse(BaseModel):
    """催还订单响应模型"""
    id: int
    order_no: str
    rental_id: int
    user_id: int
    overdue_days: int
    total_amount: float
    status: str
    is_urgent: bool
    handled_by: Optional[int]
    handled_at: Optional[datetime]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SMSLogResponse(BaseModel):
    """短信日志响应模型"""
    id: int
    phone: str
    template_code: Optional[str]
    content: str
    status: str
    provider_response: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """登录令牌模型"""
    access_token: str
    token_type: str
    user: UserResponse


class APIResponse(BaseModel):
    """通用API响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    code: int = 200
    message: str = "success"
    data: dict = {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 10,
        "total_pages": 0
    }
