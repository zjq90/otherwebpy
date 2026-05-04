from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.activity import ActivityStatus, ActivityType


class ActivityBase(BaseModel):
    """
    活动基础模型
    包含活动的基本信息字段
    """
    title: str = Field(..., min_length=2, max_length=200, description="活动标题")
    description: Optional[str] = Field(None, description="活动详细描述")
    activity_type: str = Field(default=ActivityType.OTHER.value, description="活动类型")
    start_time: datetime = Field(..., description="活动开始时间")
    end_time: datetime = Field(..., description="活动结束时间")
    registration_deadline: Optional[datetime] = Field(None, description="报名截止时间")
    location: Optional[str] = Field(None, max_length=200, description="活动地点")
    max_participants: Optional[int] = Field(None, ge=0, description="最大参与人数")
    image_url: Optional[str] = Field(None, max_length=500, description="活动图片URL")
    contact_name: Optional[str] = Field(None, max_length=50, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    is_featured: bool = Field(default=False, description="是否为推荐活动")


class ActivityCreate(ActivityBase):
    """
    活动创建模型
    用于创建新活动时的请求体
    """
    pass


class ActivityUpdate(BaseModel):
    """
    活动更新模型
    用于更新活动信息时的请求体
    """
    title: Optional[str] = Field(None, min_length=2, max_length=200, description="活动标题")
    description: Optional[str] = Field(None, description="活动详细描述")
    activity_type: Optional[str] = Field(None, description="活动类型")
    status: Optional[str] = Field(None, description="活动状态")
    start_time: Optional[datetime] = Field(None, description="活动开始时间")
    end_time: Optional[datetime] = Field(None, description="活动结束时间")
    registration_deadline: Optional[datetime] = Field(None, description="报名截止时间")
    location: Optional[str] = Field(None, max_length=200, description="活动地点")
    max_participants: Optional[int] = Field(None, ge=0, description="最大参与人数")
    image_url: Optional[str] = Field(None, max_length=500, description="活动图片URL")
    contact_name: Optional[str] = Field(None, max_length=50, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    is_featured: Optional[bool] = Field(None, description="是否为推荐活动")


class ActivityResponse(ActivityBase):
    """
    活动响应模型
    用于返回活动信息时的响应体
    """
    id: int = Field(..., description="活动ID")
    status: str = Field(..., description="活动状态")
    organizer_id: int = Field(..., description="活动发布人ID")
    current_participants: int = Field(..., description="当前报名人数")
    views_count: int = Field(..., description="浏览次数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class ActivityRegistrationBase(BaseModel):
    """
    活动报名基础模型
    包含活动报名的基本信息字段
    """
    participant_name: str = Field(..., max_length=50, description="参与者姓名")
    participant_phone: str = Field(..., max_length=20, description="联系电话")
    participant_count: int = Field(default=1, ge=1, description="参与人数")
    room_number: Optional[str] = Field(None, max_length=20, description="房间号")
    remarks: Optional[str] = Field(None, max_length=500, description="备注信息")


class ActivityRegistrationCreate(ActivityRegistrationBase):
    """
    活动报名创建模型
    用于创建新活动报名时的请求体
    """
    pass


class ActivityRegistrationResponse(ActivityRegistrationBase):
    """
    活动报名响应模型
    用于返回活动报名信息时的响应体
    """
    id: int = Field(..., description="报名ID")
    activity_id: int = Field(..., description="活动ID")
    user_id: int = Field(..., description="报名用户ID")
    is_attended: bool = Field(..., description="是否实际参加")
    created_at: datetime = Field(..., description="报名时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
