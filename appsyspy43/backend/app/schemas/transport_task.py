"""
运输任务数据验证模型
定义运输任务相关的请求和响应数据结构
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.transport_task import TaskStatus


class TransportTaskBase(BaseModel):
    """
    运输任务基础模型
    包含运输任务的基本信息字段
    """
    task_name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    task_description: Optional[str] = Field(default=None, description="任务描述")
    cargo_name: str = Field(..., min_length=1, max_length=200, description="货物名称")
    cargo_weight: Optional[Decimal] = Field(default=None, ge=0, description="货物重量（吨）")
    cargo_volume: Optional[Decimal] = Field(default=None, ge=0, description="货物体积（立方米）")
    cargo_quantity: Optional[int] = Field(default=None, ge=0, description="货物数量")
    
    # 装货地点
    loading_address: str = Field(..., min_length=1, max_length=500, description="装货地址")
    loading_latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90, description="装货纬度")
    loading_longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180, description="装货经度")
    loading_contact: Optional[str] = Field(default=None, max_length=50, description="装货联系人")
    loading_phone: Optional[str] = Field(default=None, max_length=20, description="装货联系电话")
    
    # 卸货地点
    unloading_address: str = Field(..., min_length=1, max_length=500, description="卸货地址")
    unloading_latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90, description="卸货纬度")
    unloading_longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180, description="卸货经度")
    unloading_contact: str = Field(..., min_length=1, max_length=50, description="卸货联系人")
    unloading_phone: str = Field(..., min_length=1, max_length=20, description="卸货联系电话")
    
    # 时间安排
    scheduled_departure_time: Optional[datetime] = Field(default=None, description="计划出发时间")
    scheduled_arrival_time: Optional[datetime] = Field(default=None, description="计划到达时间")
    
    # 备注
    remarks: Optional[str] = Field(default=None, description="备注信息")

    class Config:
        from_attributes = True


class TransportTaskCreate(TransportTaskBase):
    """
    运输任务创建模型
    用于创建新运输任务时的数据验证
    """
    pass


class TransportTaskUpdate(BaseModel):
    """
    运输任务更新模型
    用于更新运输任务信息时的数据验证
    """
    task_name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="任务名称")
    task_description: Optional[str] = Field(default=None, description="任务描述")
    cargo_name: Optional[str] = Field(default=None, min_length=1, max_length=200, description="货物名称")
    cargo_weight: Optional[Decimal] = Field(default=None, ge=0, description="货物重量（吨）")
    cargo_volume: Optional[Decimal] = Field(default=None, ge=0, description="货物体积（立方米）")
    cargo_quantity: Optional[int] = Field(default=None, ge=0, description="货物数量")
    loading_address: Optional[str] = Field(default=None, min_length=1, max_length=500, description="装货地址")
    loading_latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90, description="装货纬度")
    loading_longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180, description="装货经度")
    loading_contact: Optional[str] = Field(default=None, max_length=50, description="装货联系人")
    loading_phone: Optional[str] = Field(default=None, max_length=20, description="装货联系电话")
    unloading_address: Optional[str] = Field(default=None, min_length=1, max_length=500, description="卸货地址")
    unloading_latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90, description="卸货纬度")
    unloading_longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180, description="卸货经度")
    unloading_contact: Optional[str] = Field(default=None, min_length=1, max_length=50, description="卸货联系人")
    unloading_phone: Optional[str] = Field(default=None, min_length=1, max_length=20, description="卸货联系电话")
    scheduled_departure_time: Optional[datetime] = Field(default=None, description="计划出发时间")
    scheduled_arrival_time: Optional[datetime] = Field(default=None, description="计划到达时间")
    remarks: Optional[str] = Field(default=None, description="备注信息")

    class Config:
        from_attributes = True


class TaskAssignRequest(BaseModel):
    """
    任务分配请求模型
    用于调度员分配任务给司机
    """
    vehicle_id: int = Field(..., description="车辆ID")
    driver_id: int = Field(..., description="司机ID")

    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": 1,
                "driver_id": 3
            }
        }


class TaskStatusUpdateRequest(BaseModel):
    """
    任务状态更新请求模型
    用于司机更新运输任务状态
    """
    new_status: TaskStatus = Field(..., description="新状态")
    description: Optional[str] = Field(default=None, description="状态更新描述")
    latitude: Optional[Decimal] = Field(default=None, ge=-90, le=90, description="当前纬度")
    longitude: Optional[Decimal] = Field(default=None, ge=-180, le=180, description="当前经度")
    address: Optional[str] = Field(default=None, max_length=500, description="当前地址")

    class Config:
        json_schema_extra = {
            "example": {
                "new_status": "departed",
                "description": "已从仓库出发",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": "北京市朝阳区"
            }
        }


class TransportTaskResponse(BaseModel):
    """
    运输任务响应模型
    用于返回运输任务完整信息
    """
    id: int = Field(description="任务ID")
    task_no: str = Field(description="任务编号")
    task_name: str = Field(description="任务名称")
    task_description: Optional[str] = Field(default=None, description="任务描述")
    cargo_name: str = Field(description="货物名称")
    cargo_weight: Optional[Decimal] = Field(default=None, description="货物重量（吨）")
    cargo_volume: Optional[Decimal] = Field(default=None, description="货物体积（立方米）")
    cargo_quantity: Optional[int] = Field(default=None, description="货物数量")
    
    # 装货地点
    loading_address: str = Field(description="装货地址")
    loading_latitude: Optional[Decimal] = Field(default=None, description="装货纬度")
    loading_longitude: Optional[Decimal] = Field(default=None, description="装货经度")
    loading_contact: Optional[str] = Field(default=None, description="装货联系人")
    loading_phone: Optional[str] = Field(default=None, description="装货联系电话")
    
    # 卸货地点
    unloading_address: str = Field(description="卸货地址")
    unloading_latitude: Optional[Decimal] = Field(default=None, description="卸货纬度")
    unloading_longitude: Optional[Decimal] = Field(default=None, description="卸货经度")
    unloading_contact: str = Field(description="卸货联系人")
    unloading_phone: str = Field(description="卸货联系电话")
    
    # 时间信息
    scheduled_departure_time: Optional[datetime] = Field(default=None, description="计划出发时间")
    scheduled_arrival_time: Optional[datetime] = Field(default=None, description="计划到达时间")
    estimated_arrival_time: Optional[datetime] = Field(default=None, description="预计到达时间")
    actual_departure_time: Optional[datetime] = Field(default=None, description="实际出发时间")
    actual_arrival_time: Optional[datetime] = Field(default=None, description="实际到达时间")
    actual_unload_time: Optional[datetime] = Field(default=None, description="实际卸料时间")
    completed_time: Optional[datetime] = Field(default=None, description="完成时间")
    
    # 其他信息
    unload_photos: Optional[str] = Field(default=None, description="卸料照片路径")
    remarks: Optional[str] = Field(default=None, description="备注信息")
    
    # 关联信息
    vehicle_id: Optional[int] = Field(default=None, description="车辆ID")
    driver_id: Optional[int] = Field(default=None, description="司机ID")
    dispatcher_id: Optional[int] = Field(default=None, description="调度员ID")
    
    # 状态
    status: TaskStatus = Field(description="任务状态")
    
    # 时间戳
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "task_no": "TASK202401010001",
                "task_name": "钢材运输任务",
                "task_description": "运输10吨钢材到工地",
                "cargo_name": "钢材",
                "cargo_weight": 10.0,
                "cargo_volume": 5.0,
                "cargo_quantity": 100,
                "loading_address": "北京市朝阳区钢材仓库",
                "loading_latitude": 39.9042,
                "loading_longitude": 116.4074,
                "loading_contact": "张经理",
                "loading_phone": "13800138001",
                "unloading_address": "北京市海淀区建筑工地",
                "unloading_latitude": 39.9542,
                "unloading_longitude": 116.3074,
                "unloading_contact": "李工长",
                "unloading_phone": "13800138002",
                "scheduled_departure_time": "2024-01-01T08:00:00",
                "scheduled_arrival_time": "2024-01-01T10:00:00",
                "estimated_arrival_time": "2024-01-01T09:45:00",
                "actual_departure_time": "2024-01-01T08:15:00",
                "actual_arrival_time": None,
                "actual_unload_time": None,
                "completed_time": None,
                "unload_photos": None,
                "remarks": "请小心运输，避免钢材损坏",
                "vehicle_id": 1,
                "driver_id": 3,
                "dispatcher_id": 2,
                "status": "in_transit",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T08:15:00"
            }
        }


class TransportTaskListResponse(BaseModel):
    """
    运输任务列表响应模型
    用于返回运输任务列表数据
    """
    items: list[TransportTaskResponse] = Field(description="任务列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")

    class Config:
        from_attributes = True


class TaskSimpleResponse(BaseModel):
    """
    任务简易响应模型
    用于显示在地图或列表中的简要信息
    """
    id: int = Field(description="任务ID")
    task_no: str = Field(description="任务编号")
    task_name: str = Field(description="任务名称")
    cargo_name: str = Field(description="货物名称")
    unloading_address: str = Field(description="卸货地址")
    status: TaskStatus = Field(description="任务状态")
    vehicle_id: Optional[int] = Field(default=None, description="车辆ID")
    driver_id: Optional[int] = Field(default=None, description="司机ID")
    estimated_arrival_time: Optional[datetime] = Field(default=None, description="预计到达时间")

    class Config:
        from_attributes = True
