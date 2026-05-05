"""
任务更新数据验证模型
定义任务更新相关的请求和响应数据结构
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.transport_task import TaskStatus


class TaskUpdateBase(BaseModel):
    """
    任务更新基础模型
    包含任务更新的基本信息字段
    """
    transport_task_id: int = Field(..., description="任务ID")
    old_status: Optional[TaskStatus] = Field(default=None, description="变更前状态")
    new_status: TaskStatus = Field(..., description="变更后状态")
    update_type: str = Field(..., min_length=1, max_length=50, description="更新类型")
    description: Optional[str] = Field(default=None, description="更新描述")
    photo_paths: Optional[str] = Field(default=None, description="照片路径（多个用逗号分隔）")
    latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90, description="操作时纬度")
    longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180, description="操作时经度")
    address: Optional[str] = Field(default=None, max_length=500, description="操作时地址")

    class Config:
        from_attributes = True


class TaskUpdateCreate(TaskUpdateBase):
    """
    任务更新创建模型
    用于创建新任务更新时的数据验证
    """
    pass


class TaskUpdateResponse(BaseModel):
    """
    任务更新响应模型
    用于返回任务更新完整信息
    """
    id: int = Field(description="更新记录ID")
    transport_task_id: int = Field(description="任务ID")
    user_id: int = Field(description="操作人ID")
    old_status: Optional[TaskStatus] = Field(default=None, description="变更前状态")
    new_status: TaskStatus = Field(description="变更后状态")
    update_type: str = Field(description="更新类型")
    description: Optional[str] = Field(default=None, description="更新描述")
    photo_paths: Optional[str] = Field(default=None, description="照片路径")
    latitude: Optional[Decimal] = Field(default=None, description="操作时纬度")
    longitude: Optional[Decimal] = Field(default=None, description="操作时经度")
    address: Optional[str] = Field(default=None, description="操作时地址")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "transport_task_id": 1,
                "user_id": 3,
                "old_status": "assigned",
                "new_status": "departed",
                "update_type": "status_change",
                "description": "已从仓库出发前往目的地",
                "photo_paths": None,
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": "北京市朝阳区钢材仓库",
                "created_at": "2024-01-01T08:15:00"
            }
        }


class TaskUpdateListResponse(BaseModel):
    """
    任务更新列表响应模型
    用于返回任务更新列表数据
    """
    items: List[TaskUpdateResponse] = Field(description="更新记录列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")

    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    """
    照片上传响应模型
    用于返回照片上传结果
    """
    file_name: str = Field(description="文件名")
    file_path: str = Field(description="文件路径")
    file_size: int = Field(description="文件大小（字节）")
    content_type: str = Field(description="文件类型")
    access_url: str = Field(description="访问URL")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "file_name": "unload_20240101_001.jpg",
                "file_path": "/uploads/unload/unload_20240101_001.jpg",
                "file_size": 1024000,
                "content_type": "image/jpeg",
                "access_url": "http://localhost:8000/uploads/unload/unload_20240101_001.jpg"
            }
        }


class TaskDetailWithUpdates(BaseModel):
    """
    任务详情带更新记录模型
    用于返回任务详情及其所有更新记录
    """
    task: "TransportTaskResponse" = Field(description="任务信息")
    updates: List[TaskUpdateResponse] = Field(description="更新记录列表")

    class Config:
        from_attributes = True


# 避免循环导入，延迟导入
from app.schemas.transport_task import TransportTaskResponse
TaskDetailWithUpdates.model_rebuild()
