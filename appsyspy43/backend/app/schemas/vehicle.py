"""
车辆数据验证模型
定义车辆相关的请求和响应数据结构
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.vehicle import VehicleStatus, VehicleType


class VehicleBase(BaseModel):
    """
    车辆基础模型
    包含车辆的基本信息字段
    """
    plate_number: str = Field(..., min_length=1, max_length=20, description="车牌号")
    vehicle_name: str = Field(..., min_length=1, max_length=100, description="车辆名称")
    vehicle_type: VehicleType = Field(default=VehicleType.TRUCK, description="车辆类型")
    load_capacity: Optional[Decimal] = Field(default=None, ge=0, description="载重能力（吨）")
    volume: Optional[Decimal] = Field(default=None, ge=0, description="容积（立方米）")
    driver_id: Optional[int] = Field(default=None, description="当前司机ID")

    class Config:
        from_attributes = True


class VehicleCreate(VehicleBase):
    """
    车辆创建模型
    用于创建新车辆时的数据验证
    """
    pass


class VehicleUpdate(BaseModel):
    """
    车辆更新模型
    用于更新车辆信息时的数据验证
    """
    plate_number: Optional[str] = Field(default=None, min_length=1, max_length=20, description="车牌号")
    vehicle_name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="车辆名称")
    vehicle_type: Optional[VehicleType] = Field(default=None, description="车辆类型")
    load_capacity: Optional[Decimal] = Field(default=None, ge=0, description="载重能力（吨）")
    volume: Optional[Decimal] = Field(default=None, ge=0, description="容积（立方米）")
    driver_id: Optional[int] = Field(default=None, description="当前司机ID")
    status: Optional[VehicleStatus] = Field(default=None, description="车辆状态")

    class Config:
        from_attributes = True


class VehicleLocationUpdate(BaseModel):
    """
    车辆位置更新模型
    用于实时更新车辆位置信息
    """
    latitude: Decimal = Field(..., ge=-90, le=90, description="纬度")
    longitude: Decimal = Field(..., ge=-180, le=180, description="经度")
    address: Optional[str] = Field(default=None, max_length=255, description="当前地址")
    speed: Optional[Decimal] = Field(default=None, ge=0, description="速度（km/h）")
    direction: Optional[Decimal] = Field(default=None, ge=0, le=360, description="方向（角度）")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": "北京市朝阳区",
                "speed": 60.5,
                "direction": 90.0
            }
        }


class VehicleResponse(BaseModel):
    """
    车辆响应模型
    用于返回车辆完整信息
    """
    id: int = Field(description="车辆ID")
    plate_number: str = Field(description="车牌号")
    vehicle_name: str = Field(description="车辆名称")
    vehicle_type: VehicleType = Field(description="车辆类型")
    load_capacity: Optional[Decimal] = Field(default=None, description="载重能力（吨）")
    volume: Optional[Decimal] = Field(default=None, description="容积（立方米）")
    driver_id: Optional[int] = Field(default=None, description="当前司机ID")
    status: VehicleStatus = Field(description="车辆状态")
    current_latitude: Optional[Decimal] = Field(default=None, description="当前纬度")
    current_longitude: Optional[Decimal] = Field(default=None, description="当前经度")
    current_address: Optional[str] = Field(default=None, description="当前地址")
    last_location_update: Optional[datetime] = Field(default=None, description="最后位置更新时间")
    created_at: datetime = Field(description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "plate_number": "京A12345",
                "vehicle_name": "重型卡车一号",
                "vehicle_type": "truck",
                "load_capacity": 20.0,
                "volume": 50.0,
                "driver_id": 3,
                "status": "idle",
                "current_latitude": 39.9042,
                "current_longitude": 116.4074,
                "current_address": "北京市朝阳区",
                "last_location_update": "2024-01-01T00:00:00",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class VehicleListResponse(BaseModel):
    """
    车辆列表响应模型
    用于返回车辆列表数据
    """
    items: list[VehicleResponse] = Field(description="车辆列表")
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")

    class Config:
        from_attributes = True


class VehicleSimpleResponse(BaseModel):
    """
    车辆简易响应模型
    用于任务分配时显示车辆列表
    """
    id: int = Field(description="车辆ID")
    plate_number: str = Field(description="车牌号")
    vehicle_name: str = Field(description="车辆名称")
    vehicle_type: VehicleType = Field(description="车辆类型")
    status: VehicleStatus = Field(description="车辆状态")
    current_latitude: Optional[Decimal] = Field(default=None, description="当前纬度")
    current_longitude: Optional[Decimal] = Field(default=None, description="当前经度")
    driver_id: Optional[int] = Field(default=None, description="当前司机ID")

    class Config:
        from_attributes = True
