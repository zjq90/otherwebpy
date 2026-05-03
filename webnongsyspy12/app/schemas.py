from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 设备相关 Schema ====================

class DeviceBase(BaseModel):
    """设备基础模型"""
    device_code: str = Field(..., min_length=1, max_length=50, description="设备编号")
    device_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    device_type: str = Field(..., min_length=1, max_length=50, description="设备类型")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    status: Optional[str] = Field("online", max_length=20, description="设备状态")
    description: Optional[str] = Field(None, description="设备描述")


class DeviceCreate(DeviceBase):
    """创建设备模型"""
    pass


class DeviceUpdate(BaseModel):
    """更新设备模型"""
    device_name: Optional[str] = Field(None, max_length=100)
    device_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None)


class DeviceResponse(DeviceBase):
    """设备响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 环境数据相关 Schema ====================

class EnvironmentDataBase(BaseModel):
    """环境数据基础模型"""
    device_id: int = Field(..., description="关联设备ID")
    temperature: Optional[float] = Field(None, ge=-40, le=85, description="空气温度（℃）")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="空气湿度（%）")
    light_intensity: Optional[float] = Field(None, ge=0, description="光照强度（Lux）")
    soil_moisture: Optional[float] = Field(None, ge=0, le=100, description="土壤水分（%）")
    co2_concentration: Optional[float] = Field(None, ge=0, description="CO₂浓度（ppm）")


class EnvironmentDataCreate(EnvironmentDataBase):
    """创建环境数据模型"""
    pass


class EnvironmentDataResponse(EnvironmentDataBase):
    """环境数据响应模型"""
    id: int
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class EnvironmentDataListResponse(BaseModel):
    """环境数据列表响应"""
    total: int
    data: List[EnvironmentDataResponse]


# ==================== 作物相关 Schema ====================

class CropBase(BaseModel):
    """作物基础模型"""
    crop_name: str = Field(..., min_length=1, max_length=100, description="作物名称")
    crop_type: Optional[str] = Field(None, max_length=50, description="作物类型")
    variety: Optional[str] = Field(None, max_length=100, description="品种")
    planting_date: Optional[datetime] = Field(None, description="种植日期")
    expected_harvest_date: Optional[datetime] = Field(None, description="预计收获日期")
    location: Optional[str] = Field(None, max_length=200, description="种植位置")
    status: Optional[str] = Field("growing", max_length=20, description="作物状态")
    notes: Optional[str] = Field(None, description="备注信息")


class CropCreate(CropBase):
    """创建作物模型"""
    pass


class CropUpdate(BaseModel):
    """更新作物模型"""
    crop_name: Optional[str] = Field(None, max_length=100)
    crop_type: Optional[str] = Field(None, max_length=50)
    variety: Optional[str] = Field(None, max_length=100)
    planting_date: Optional[datetime] = Field(None)
    expected_harvest_date: Optional[datetime] = Field(None)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None)


class CropResponse(CropBase):
    """作物响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 生长记录相关 Schema ====================

class GrowthRecordBase(BaseModel):
    """生长记录基础模型"""
    crop_id: int = Field(..., description="关联作物ID")
    record_type: str = Field(..., min_length=1, max_length=20, description="记录类型")
    title: Optional[str] = Field(None, max_length=200, description="记录标题")
    description: Optional[str] = Field(None, description="详细描述")
    growth_stage: Optional[str] = Field(None, max_length=50, description="生育期")
    recorded_at: Optional[datetime] = Field(default_factory=datetime.now, description="记录时间")


class GrowthRecordCreate(GrowthRecordBase):
    """创建生长记录模型"""
    pass


class GrowthRecordUpdate(BaseModel):
    """更新生长记录模型"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None)
    growth_stage: Optional[str] = Field(None, max_length=50)
    recorded_at: Optional[datetime] = Field(None)
    ai_diagnosis: Optional[str] = Field(None)
    disease_detected: Optional[str] = Field(None)
    nutrition_status: Optional[str] = Field(None)
    diagnosis_confidence: Optional[float] = Field(None)


class GrowthRecordResponse(GrowthRecordBase):
    """生长记录响应模型"""
    id: int
    file_path: Optional[str]
    file_type: Optional[str]
    ai_diagnosis: Optional[str]
    disease_detected: Optional[str]
    nutrition_status: Optional[str]
    diagnosis_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 统计分析相关 Schema ====================

class EnvironmentStats(BaseModel):
    """环境数据统计模型"""
    field: str
    min_value: Optional[float]
    max_value: Optional[float]
    avg_value: Optional[float]
    latest_value: Optional[float]


class TrendDataPoint(BaseModel):
    """趋势数据点模型"""
    time: datetime
    value: Optional[float]


# ==================== API 响应通用模型 ====================

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class ApiListResponse(BaseModel):
    """通用列表API响应模型"""
    success: bool = True
    message: str = "获取成功"
    total: int = 0
    data: list = []
