"""
环保合规监管模块的Pydantic数据模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# ============ 监测点位相关模型 ============

class MonitoringPointBase(BaseModel):
    """
    监测点位基础模型
    """
    point_code: Optional[str] = None
    point_name: Optional[str] = None
    location: Optional[str] = None
    monitoring_type: Optional[str] = None
    equipment_model: Optional[str] = None
    installation_date: Optional[date] = None
    status: Optional[str] = "正常"


class MonitoringPointCreate(MonitoringPointBase):
    """
    创建监测点位模型
    """
    point_code: str
    point_name: str
    monitoring_type: str


class MonitoringPointUpdate(MonitoringPointBase):
    """
    更新监测点位模型
    """
    pass


class MonitoringPointResponse(MonitoringPointBase):
    """
    监测点位响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 粉尘监测相关模型 ============

class DustMonitoringBase(BaseModel):
    """
    粉尘监测基础模型
    """
    monitoring_point_id: Optional[int] = None
    record_time: Optional[datetime] = None
    record_date: Optional[date] = None
    pm25_concentration: Optional[float] = 0.0
    pm10_concentration: Optional[float] = 0.0
    tsp_concentration: Optional[float] = 0.0
    is_over_limit: Optional[bool] = False
    threshold_value: Optional[float] = 0.15
    remarks: Optional[str] = None


class DustMonitoringCreate(DustMonitoringBase):
    """
    创建粉尘监测模型
    """
    monitoring_point_id: int


class DustMonitoringUpdate(DustMonitoringBase):
    """
    更新粉尘监测模型
    """
    pass


class DustMonitoringResponse(DustMonitoringBase):
    """
    粉尘监测响应模型
    """
    id: int
    created_at: datetime
    point_name: Optional[str] = None
    point_location: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 噪音监测相关模型 ============

class NoiseMonitoringBase(BaseModel):
    """
    噪音监测基础模型
    """
    monitoring_point_id: Optional[int] = None
    record_time: Optional[datetime] = None
    record_date: Optional[date] = None
    db_value: Optional[float] = 0.0
    frequency: Optional[str] = None
    is_over_limit: Optional[bool] = False
    threshold_value: Optional[float] = 85.0
    remarks: Optional[str] = None


class NoiseMonitoringCreate(NoiseMonitoringBase):
    """
    创建噪音监测模型
    """
    monitoring_point_id: int


class NoiseMonitoringUpdate(NoiseMonitoringBase):
    """
    更新噪音监测模型
    """
    pass


class NoiseMonitoringResponse(NoiseMonitoringBase):
    """
    噪音监测响应模型
    """
    id: int
    created_at: datetime
    point_name: Optional[str] = None
    point_location: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 废水监测相关模型 ============

class WastewaterMonitoringBase(BaseModel):
    """
    废水监测基础模型
    """
    monitoring_point_id: Optional[int] = None
    record_time: Optional[datetime] = None
    record_date: Optional[date] = None
    ph_value: Optional[float] = 7.0
    cod_value: Optional[float] = 0.0
    ss_value: Optional[float] = 0.0
    ammonia_nitrogen: Optional[float] = 0.0
    flow_rate: Optional[float] = 0.0
    is_over_limit: Optional[bool] = False
    ph_threshold_min: Optional[float] = 6.0
    ph_threshold_max: Optional[float] = 9.0
    remarks: Optional[str] = None


class WastewaterMonitoringCreate(WastewaterMonitoringBase):
    """
    创建废水监测模型
    """
    monitoring_point_id: int


class WastewaterMonitoringUpdate(WastewaterMonitoringBase):
    """
    更新废水监测模型
    """
    pass


class WastewaterMonitoringResponse(WastewaterMonitoringBase):
    """
    废水监测响应模型
    """
    id: int
    created_at: datetime
    point_name: Optional[str] = None
    point_location: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 报警记录相关模型 ============

class AlarmRecordBase(BaseModel):
    """
    报警记录基础模型
    """
    alarm_time: Optional[datetime] = None
    alarm_type: Optional[str] = None
    monitoring_point_id: Optional[int] = None
    dust_monitoring_id: Optional[int] = None
    noise_monitoring_id: Optional[int] = None
    wastewater_monitoring_id: Optional[int] = None
    alarm_level: Optional[str] = "一般"
    actual_value: Optional[float] = 0.0
    threshold_value: Optional[float] = 0.0
    message: Optional[str] = None
    is_handled: Optional[bool] = False
    handled_by: Optional[str] = None
    handled_time: Optional[datetime] = None
    handling_method: Optional[str] = None


class AlarmRecordCreate(AlarmRecordBase):
    """
    创建报警记录模型
    """
    alarm_type: str
    actual_value: float
    threshold_value: float


class AlarmRecordUpdate(AlarmRecordBase):
    """
    更新报警记录模型
    """
    pass


class AlarmRecordResponse(AlarmRecordBase):
    """
    报警记录响应模型
    """
    id: int
    created_at: datetime
    point_name: Optional[str] = None
    point_location: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 环保统计相关模型 ============

class DailyDustStats(BaseModel):
    """
    日粉尘统计
    """
    record_date: date
    monitoring_point_id: int
    point_name: str
    avg_pm25: float
    avg_pm10: float
    avg_tsp: float
    max_pm25: float
    max_pm10: float
    max_tsp: float
    over_limit_count: int
    total_records: int


class DailyNoiseStats(BaseModel):
    """
    日噪音统计
    """
    record_date: date
    monitoring_point_id: int
    point_name: str
    avg_db: float
    max_db: float
    min_db: float
    over_limit_count: int
    total_records: int


class DailyWastewaterStats(BaseModel):
    """
    日废水统计
    """
    record_date: date
    monitoring_point_id: int
    point_name: str
    avg_ph: float
    avg_cod: float
    avg_ss: float
    avg_ammonia_nitrogen: float
    total_flow: float
    over_limit_count: int
    total_records: int


class AlarmStats(BaseModel):
    """
    报警统计
    """
    record_date: date
    alarm_type: str
    total_alarms: int
    handled_alarms: int
    pending_alarms: int
    urgent_alarms: int
    important_alarms: int
    normal_alarms: int
