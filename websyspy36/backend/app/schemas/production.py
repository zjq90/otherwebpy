"""
生产数据分析模块的Pydantic数据模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# ============ 设备管理相关模型 ============

class EquipmentBase(BaseModel):
    """
    设备基础模型
    包含设备的基本字段
    """
    equipment_code: Optional[str] = None
    equipment_name: Optional[str] = None
    equipment_type: Optional[str] = None
    specification: Optional[str] = None
    max_capacity: Optional[float] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[date] = None
    status: Optional[str] = "正常"


class EquipmentCreate(EquipmentBase):
    """
    创建设备时的模型
    必须提供设备编号和名称
    """
    equipment_code: str
    equipment_name: str


class EquipmentUpdate(EquipmentBase):
    """
    更新设备时的模型
    所有字段都是可选的
    """
    pass


class EquipmentResponse(EquipmentBase):
    """
    设备响应模型
    包含从数据库返回的完整设备信息
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic配置类"""
        from_attributes = True


# ============ 生产记录相关模型 ============

class ProductionRecordBase(BaseModel):
    """
    生产记录基础模型
    """
    record_date: Optional[date] = None
    total_production: Optional[float] = 0.0
    qualified_production: Optional[float] = 0.0
    batch_count: Optional[int] = 0
    working_hours: Optional[float] = 0.0
    production_type: Optional[str] = None
    remarks: Optional[str] = None


class ProductionRecordCreate(ProductionRecordBase):
    """
    创建生产记录模型
    """
    record_date: date


class ProductionRecordUpdate(ProductionRecordBase):
    """
    更新生产记录模型
    """
    pass


class ProductionRecordResponse(ProductionRecordBase):
    """
    生产记录响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 设备利用率相关模型 ============

class EquipmentUtilizationBase(BaseModel):
    """
    设备利用率基础模型
    """
    equipment_id: Optional[int] = None
    record_date: Optional[date] = None
    total_available_hours: Optional[float] = 24.0
    actual_working_hours: Optional[float] = 0.0
    maintenance_hours: Optional[float] = 0.0
    idle_hours: Optional[float] = 0.0
    utilization_rate: Optional[float] = 0.0


class EquipmentUtilizationCreate(EquipmentUtilizationBase):
    """
    创建设备利用率模型
    """
    equipment_id: int
    record_date: date


class EquipmentUtilizationUpdate(EquipmentUtilizationBase):
    """
    更新设备利用率模型
    """
    pass


class EquipmentUtilizationResponse(EquipmentUtilizationBase):
    """
    设备利用率响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 能耗指标相关模型 ============

class EnergyConsumptionBase(BaseModel):
    """
    能耗指标基础模型
    """
    record_date: Optional[date] = None
    equipment_id: Optional[int] = None
    energy_type: Optional[str] = None
    consumption_amount: Optional[float] = 0.0
    unit: Optional[str] = None
    cost: Optional[float] = 0.0


class EnergyConsumptionCreate(EnergyConsumptionBase):
    """
    创建能耗指标模型
    """
    energy_type: str
    record_date: date


class EnergyConsumptionUpdate(EnergyConsumptionBase):
    """
    更新能耗指标模型
    """
    pass


class EnergyConsumptionResponse(EnergyConsumptionBase):
    """
    能耗指标响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 统计分析相关模型 ============

class DailyProductionStats(BaseModel):
    """
    日产量统计模型
    """
    record_date: date
    total_production: float
    qualified_production: float
    qualified_rate: float
    batch_count: int
    working_hours: float


class MonthlyProductionStats(BaseModel):
    """
    月产量统计模型
    """
    year: int
    month: int
    total_production: float
    qualified_production: float
    qualified_rate: float
    total_batches: int
    total_working_hours: float


class EquipmentUtilizationStats(BaseModel):
    """
    设备利用率统计模型
    """
    equipment_id: int
    equipment_name: str
    equipment_code: str
    total_available_hours: float
    total_working_hours: float
    total_maintenance_hours: float
    total_idle_hours: float
    average_utilization_rate: float


class EnergyConsumptionStats(BaseModel):
    """
    能耗统计模型
    """
    energy_type: str
    total_consumption: float
    total_cost: float
    unit: str
