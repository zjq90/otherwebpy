from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnnouncementBase(BaseModel):
    """公告基础模型"""
    title: str = Field(..., max_length=200, description="公告标题")
    summary: Optional[str] = Field(None, max_length=500, description="公告摘要")
    content: str = Field(..., description="公告内容")
    announcement_type: int = Field(0, description="公告类型：0-系统公告，1-环保活动，2-政策通知，3-其他")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片")
    images: Optional[str] = Field(None, description="图片列表(JSON格式)")
    status: Optional[int] = Field(0, description="发布状态：0-草稿，1-已发布，2-已撤回")
    sort: int = Field(0, description="排序")
    is_top: int = Field(0, description="是否置顶")
    publish_time: Optional[datetime] = None
    expire_time: Optional[datetime] = None
    view_count: int = Field(0, description="浏览次数")

class AnnouncementCreate(AnnouncementBase):
    """公告创建模型"""
    pass

class AnnouncementUpdate(BaseModel):
    """公告更新模型"""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    announcement_type: Optional[int] = None
    cover_image: Optional[str] = None
    images: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None
    is_top: Optional[int] = None
    publish_time: Optional[datetime] = None
    expire_time: Optional[datetime] = None

class AnnouncementResponse(AnnouncementBase):
    """公告响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
