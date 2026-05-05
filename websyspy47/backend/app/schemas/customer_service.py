from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .common import validate_phone, validate_password

class CustomerServiceStaffBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=11, description="手机号")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    group_type: int = Field(0, description="分组类型：0-普通客服，1-投诉处理，2-技术支持")
    status: Optional[int] = Field(1, description="状态：0-禁用，1-正常，2-离线")

    @field_validator('phone')
    @classmethod
    def validate_phone_field(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

class CustomerServiceStaffCreate(CustomerServiceStaffBase):
    password: str = Field(..., min_length=6, max_length=20, description="密码")

    @field_validator('password')
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        return validate_password(v, is_new=True)

class CustomerServiceStaffUpdate(BaseModel):
    real_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    group_type: Optional[int] = None
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

class CustomerServiceStaffResponse(CustomerServiceStaffBase):
    """客服人员响应模型"""
    id: int
    total_consultations: int = 0
    resolved_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConsultationBase(BaseModel):
    """咨询基础模型"""
    consultation_no: str = Field(..., max_length=50, description="咨询编号")
    user_id: int
    user_name: Optional[str] = Field(None, max_length=50, description="用户姓名")
    user_phone: Optional[str] = Field(None, max_length=20, description="用户电话")
    cs_staff_id: Optional[int] = None
    cs_staff_name: Optional[str] = Field(None, max_length=50, description="客服人员姓名")
    consultation_type: int = Field(0, description="咨询类型：0-订单问题，1-积分问题，2-回收问题，3-其他")
    title: Optional[str] = Field(None, max_length=200, description="标题")
    question: str = Field(..., description="问题描述")
    status: Optional[int] = Field(0, description="状态：0-待分配，1-处理中，2-已解决，3-已关闭")
    rating: Optional[int] = None
    rating_comment: Optional[str] = None

class ConsultationCreate(ConsultationBase):
    """咨询创建模型"""
    pass

class ConsultationUpdate(BaseModel):
    """咨询更新模型"""
    cs_staff_id: Optional[int] = None
    cs_staff_name: Optional[str] = None
    consultation_type: Optional[int] = None
    title: Optional[str] = None
    question: Optional[str] = None
    status: Optional[int] = None
    rating: Optional[int] = None
    rating_comment: Optional[str] = None

class ConsultationResponse(ConsultationBase):
    """咨询响应模型"""
    id: int
    assign_time: Optional[datetime] = None
    resolve_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ConsultationMessageBase(BaseModel):
    """咨询消息基础模型"""
    consultation_id: int
    sender_type: int = Field(..., description="发送者类型：0-用户，1-客服")
    sender_id: Optional[int] = None
    sender_name: Optional[str] = Field(None, max_length=50, description="发送者名称")
    message_type: int = Field(0, description="消息类型：0-文本，1-图片，2-文件")
    content: str = Field(..., description="消息内容")
    is_read: int = Field(0, description="是否已读")

class ConsultationMessageCreate(ConsultationMessageBase):
    """咨询消息创建模型"""
    pass

class ConsultationMessageResponse(ConsultationMessageBase):
    """咨询消息响应模型"""
    id: int
    read_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
