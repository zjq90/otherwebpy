from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.service_request import ServiceType, ServiceStatus


class ServiceRequestBase(BaseModel):
    """
    服务请求基础模型
    包含服务请求的基本信息字段
    """
    title: str = Field(..., min_length=2, max_length=200, description="请求标题")
    description: Optional[str] = Field(None, description="请求描述详情")
    service_type: str = Field(..., description="服务类型：repair/complaint/consult")
    room_number: Optional[str] = Field(None, max_length=20, description="房间号")
    contact_name: Optional[str] = Field(None, max_length=50, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    priority: int = Field(default=1, ge=1, le=3, description="优先级：1-普通，2-紧急，3-非常紧急")
    location: Optional[str] = Field(None, max_length=100, description="具体位置描述")


class ServiceRequestCreate(ServiceRequestBase):
    """
    服务请求创建模型
    用于创建新服务请求时的请求体
    """
    pass


class ServiceRequestUpdate(BaseModel):
    """
    服务请求更新模型
    用于更新服务请求信息时的请求体
    """
    title: Optional[str] = Field(None, min_length=2, max_length=200, description="请求标题")
    description: Optional[str] = Field(None, description="请求描述详情")
    status: Optional[str] = Field(None, description="状态")
    assignee_id: Optional[int] = Field(None, description="处理人ID")
    contact_name: Optional[str] = Field(None, max_length=50, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    priority: Optional[int] = Field(None, ge=1, le=3, description="优先级")
    location: Optional[str] = Field(None, max_length=100, description="具体位置描述")


class ServiceRequestResponse(ServiceRequestBase):
    """
    服务请求响应模型
    用于返回服务请求信息时的响应体
    """
    id: int = Field(..., description="服务请求ID")
    status: str = Field(..., description="状态")
    user_id: int = Field(..., description="提交用户ID")
    assignee_id: Optional[int] = Field(None, description="处理人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    class Config:
        from_attributes = True


class ServiceProgressBase(BaseModel):
    """
    服务进度基础模型
    包含服务进度的基本信息字段
    """
    action: str = Field(..., max_length=50, description="操作类型")
    description: Optional[str] = Field(None, description="进度描述")


class ServiceProgressCreate(ServiceProgressBase):
    """
    服务进度创建模型
    用于创建新服务进度时的请求体
    """
    pass


class ServiceProgressResponse(ServiceProgressBase):
    """
    服务进度响应模型
    用于返回服务进度信息时的响应体
    """
    id: int = Field(..., description="进度记录ID")
    service_request_id: int = Field(..., description="服务请求ID")
    operator_id: int = Field(..., description="操作人ID")
    from_status: Optional[str] = Field(None, description="变更前状态")
    to_status: Optional[str] = Field(None, description="变更后状态")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
