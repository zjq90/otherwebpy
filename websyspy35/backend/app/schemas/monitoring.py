from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class SensorDataBase(BaseModel):
    """
    传感器数据基础模型
    """
    sensor_id: int = Field(..., description="关联传感器ID")
    value: float = Field(..., description="采集数值")
    status: Optional[str] = Field("正常", max_length=20, description="数据状态")
    is_abnormal: Optional[bool] = Field(False, description="是否异常")
    description: Optional[str] = Field(None, description="备注信息")


class SensorDataCreate(SensorDataBase):
    """
    传感器数据创建模型
    """
    collected_at: Optional[datetime] = Field(None, description="采集时间")


class SensorDataResponse(SensorDataBase):
    """
    传感器数据响应模型
    """
    id: int = Field(..., description="数据ID")
    collected_at: datetime = Field(..., description="采集时间")
    
    class Config:
        from_attributes = True


class OperationLogBase(BaseModel):
    """
    运行日志基础模型
    """
    equipment_id: int = Field(..., description="关联设备ID")
    log_type: str = Field(..., min_length=1, max_length=50, description="日志类型")
    level: Optional[str] = Field("信息", max_length=20, description="日志级别")
    title: str = Field(..., min_length=1, max_length=200, description="日志标题")
    content: Optional[str] = Field(None, description="日志内容")
    from_status: Optional[str] = Field(None, max_length=50, description="原始状态")
    to_status: Optional[str] = Field(None, max_length=50, description="目标状态")
    related_sensor_data_id: Optional[int] = Field(None, description="关联传感器数据ID")
    description: Optional[str] = Field(None, description="备注信息")


class OperationLogCreate(OperationLogBase):
    """
    运行日志创建模型
    """
    recorded_at: Optional[datetime] = Field(None, description="记录时间")


class OperationLogResponse(OperationLogBase):
    """
    运行日志响应模型
    """
    id: int = Field(..., description="日志ID")
    recorded_at: datetime = Field(..., description="记录时间")
    
    class Config:
        from_attributes = True


class ControlSystemStatusBase(BaseModel):
    """
    控制系统监控基础模型
    """
    monitor_item: str = Field(..., min_length=1, max_length=100, description="监控项名称")
    monitor_type: str = Field(..., min_length=1, max_length=50, description="监控项类型")
    current_value: Optional[str] = Field(None, max_length=200, description="当前状态值")
    numeric_value: Optional[float] = Field(None, description="数值类型值")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    normal_status: Optional[str] = Field(None, max_length=200, description="正常状态描述")
    status: Optional[str] = Field("正常", max_length=20, description="当前状态")
    is_enabled: Optional[bool] = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="备注信息")


class ControlSystemStatusCreate(ControlSystemStatusBase):
    """
    控制系统监控创建模型
    """
    pass


class ControlSystemStatusUpdate(BaseModel):
    """
    控制系统监控更新模型
    """
    monitor_item: Optional[str] = Field(None, min_length=1, max_length=100, description="监控项名称")
    monitor_type: Optional[str] = Field(None, min_length=1, max_length=50, description="监控项类型")
    current_value: Optional[str] = Field(None, max_length=200, description="当前状态值")
    numeric_value: Optional[float] = Field(None, description="数值类型值")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    normal_status: Optional[str] = Field(None, max_length=200, description="正常状态描述")
    status: Optional[str] = Field(None, max_length=20, description="当前状态")
    is_enabled: Optional[bool] = Field(None, description="是否启用")
    last_checked_at: Optional[datetime] = Field(None, description="最后检查时间")
    description: Optional[str] = Field(None, description="备注信息")


class ControlSystemStatusResponse(ControlSystemStatusBase):
    """
    控制系统监控响应模型
    """
    id: int = Field(..., description="监控项ID")
    last_checked_at: datetime = Field(..., description="最后检查时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True
