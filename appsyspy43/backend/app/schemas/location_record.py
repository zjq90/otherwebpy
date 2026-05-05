"""
位置记录数据验证模型
定义位置记录相关的请求和响应数据结构
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class LocationRecordBase(BaseModel):
    """
    位置记录基础模型
    包含位置记录的基本信息字段
    """
    vehicle_id: int = Field(..., description="车辆ID")
    user_id: Optional[int] = Field(default=None, description="司机用户ID")
    transport_task_id: Optional[int] = Field(default=None, description="关联任务ID")
    latitude: Decimal = Field(..., ge=-90, le=90, description="纬度")
    longitude: Decimal = Field(..., ge=-180, le=180, description="经度")
    address: Optional[str] = Field(default=None, max_length=500, description="地址描述")
    speed: Optional[Decimal] = Field(default=None, ge=0, description="速度（km/h）")
    direction: Optional[Decimal] = Field(default=None, ge=0, le=360, description="方向（角度）")
    accuracy: Optional[Decimal] = Field(default=None, ge=0, description="定位精度（米）")
    device_type: Optional[str] = Field(default=None, max_length=50, description="设备类型")
    device_id: Optional[str] = Field(default=None, max_length=100, description="设备唯一标识")

    class Config:
        from_attributes = True


class LocationRecordCreate(LocationRecordBase):
    """
    位置记录创建模型
    用于创建新位置记录时的数据验证
    """
    pass


class LocationBatchCreate(BaseModel):
    """
    批量位置记录创建模型
    用于批量上传位置记录
    """
    locations: List[LocationRecordCreate] = Field(..., description="位置记录列表")

    class Config:
        json_schema_extra = {
            "example": {
                "locations": [
                    {
                        "vehicle_id": 1,
                        "user_id": 3,
                        "transport_task_id": 1,
                        "latitude": 39.9042,
                        "longitude": 116.4074,
                        "address": "北京市朝阳区",
                        "speed": 60.5,
                        "direction": 90.0
                    },
                    {
                        "vehicle_id": 1,
                        "user_id": 3,
                        "transport_task_id": 1,
                        "latitude": 39.9142,
                        "longitude": 116.4174,
                        "address": "北京市朝阳区",
                        "speed": 65.0,
                        "direction": 90.0
                    }
                ]
            }
        }


class LocationRecordResponse(BaseModel):
    """
    位置记录响应模型
    用于返回位置记录完整信息
    """
    id: int = Field(description="记录ID")
    vehicle_id: int = Field(description="车辆ID")
    user_id: Optional[int] = Field(default=None, description="司机用户ID")
    transport_task_id: Optional[int] = Field(default=None, description="关联任务ID")
    latitude: Decimal = Field(description="纬度")
    longitude: Decimal = Field(description="经度")
    address: Optional[str] = Field(default=None, description="地址描述")
    speed: Optional[Decimal] = Field(default=None, description="速度（km/h）")
    direction: Optional[Decimal] = Field(default=None, description="方向（角度）")
    accuracy: Optional[Decimal] = Field(default=None, description="定位精度（米）")
    device_type: Optional[str] = Field(default=None, description="设备类型")
    device_id: Optional[str] = Field(default=None, description="设备唯一标识")
    recorded_at: datetime = Field(description="记录时间")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "vehicle_id": 1,
                "user_id": 3,
                "transport_task_id": 1,
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": "北京市朝阳区",
                "speed": 60.5,
                "direction": 90.0,
                "accuracy": 10.0,
                "device_type": "GPS",
                "device_id": "device-001",
                "recorded_at": "2024-01-01T08:00:00",
                "created_at": "2024-01-01T08:00:00"
            }
        }


class LocationRecordListResponse(BaseModel):
    """
    位置记录列表响应模型
    用于返回位置记录列表数据
    """
    items: List[LocationRecordResponse] = Field(description="位置记录列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")

    class Config:
        from_attributes = True


class TrajectoryPoint(BaseModel):
    """
    轨迹点模型
    用于轨迹回放时的简化数据结构
    """
    latitude: Decimal = Field(description="纬度")
    longitude: Decimal = Field(description="经度")
    address: Optional[str] = Field(default=None, description="地址描述")
    speed: Optional[Decimal] = Field(default=None, description="速度（km/h）")
    recorded_at: datetime = Field(description="记录时间")

    class Config:
        from_attributes = True


class TrajectoryResponse(BaseModel):
    """
    轨迹响应模型
    用于返回车辆行驶轨迹
    """
    vehicle_id: int = Field(description="车辆ID")
    transport_task_id: Optional[int] = Field(default=None, description="关联任务ID")
    start_time: datetime = Field(description="轨迹开始时间")
    end_time: datetime = Field(description="轨迹结束时间")
    points: List[TrajectoryPoint] = Field(description="轨迹点列表")
    total_distance: Optional[Decimal] = Field(default=None, description="总距离（公里）")
    total_points: int = Field(description="轨迹点数量")

    class Config:
        from_attributes = True
