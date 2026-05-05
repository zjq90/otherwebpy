from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class EquipmentBase(BaseModel):
    equipment_no: str
    equipment_name: str
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    status: str = "正常"
    responsible_person: Optional[str] = None
    remarks: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    equipment_no: Optional[str] = None
    equipment_name: Optional[str] = None
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    status: Optional[str] = None
    responsible_person: Optional[str] = None
    remarks: Optional[str] = None

class EquipmentResponse(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentRuntimeBase(BaseModel):
    equipment_id: int
    record_date: date
    planned_runtime: float = 24.0
    actual_runtime: float = 0.0
    downtime: float = 0.0
    standby_time: float = 0.0
    operator: Optional[str] = None
    remarks: Optional[str] = None

class EquipmentRuntimeCreate(EquipmentRuntimeBase):
    pass

class EquipmentRuntimeUpdate(BaseModel):
    equipment_id: Optional[int] = None
    record_date: Optional[date] = None
    planned_runtime: Optional[float] = None
    actual_runtime: Optional[float] = None
    downtime: Optional[float] = None
    standby_time: Optional[float] = None
    operator: Optional[str] = None
    remarks: Optional[str] = None

class EquipmentRuntimeResponse(EquipmentRuntimeBase):
    id: int
    operating_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentFaultBase(BaseModel):
    equipment_id: int
    fault_date: date
    fault_type: Optional[str] = None
    fault_description: Optional[str] = None
    fault_level: str = "一般"
    downtime_duration: float = 0.0
    repair_person: Optional[str] = None
    repair_cost: float = 0.0
    status: str = "已修复"
    remarks: Optional[str] = None

class EquipmentFaultCreate(EquipmentFaultBase):
    pass

class EquipmentFaultUpdate(BaseModel):
    equipment_id: Optional[int] = None
    fault_date: Optional[date] = None
    fault_type: Optional[str] = None
    fault_description: Optional[str] = None
    fault_level: Optional[str] = None
    downtime_duration: Optional[float] = None
    repair_person: Optional[str] = None
    repair_cost: Optional[float] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class EquipmentFaultResponse(EquipmentFaultBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentMaintenanceBase(BaseModel):
    equipment_id: int
    plan_date: date
    actual_date: Optional[date] = None
    maintenance_type: Optional[str] = None
    maintenance_content: Optional[str] = None
    maintenance_person: Optional[str] = None
    status: str = "待执行"
    is_completed: int = 0
    remarks: Optional[str] = None

class EquipmentMaintenanceCreate(EquipmentMaintenanceBase):
    pass

class EquipmentMaintenanceUpdate(BaseModel):
    equipment_id: Optional[int] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    maintenance_type: Optional[str] = None
    maintenance_content: Optional[str] = None
    maintenance_person: Optional[str] = None
    status: Optional[str] = None
    is_completed: Optional[int] = None
    remarks: Optional[str] = None

class EquipmentMaintenanceResponse(EquipmentMaintenanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EquipmentOperatingRateItem(BaseModel):
    date: str
    equipment_name: str
    operating_rate: float
    actual_runtime: float
    downtime: float

class EquipmentOperatingRateResponse(BaseModel):
    period: str
    avg_operating_rate: float
    total_downtime: float
    data: List[EquipmentOperatingRateItem]

class MaintenanceRateItem(BaseModel):
    date: str
    planned_count: int
    completed_count: int
    completion_rate: float

class MaintenanceRateResponse(BaseModel):
    period: str
    total_planned: int
    total_completed: int
    avg_completion_rate: float
    data: List[MaintenanceRateItem]
