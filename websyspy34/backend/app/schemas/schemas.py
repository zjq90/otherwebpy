from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.models import (
    FormulaStatus, ProductionStatus, ResourceType, 
    ResourceStatus, AlertLevel, AlertStatus, ProductionStage
)


class FormulaBase(BaseModel):
    formula_code: str = Field(..., max_length=50, description="配方编码")
    formula_name: str = Field(..., max_length=100, description="配方名称")
    concrete_type: str = Field(..., max_length=50, description="混凝土类型")
    strength_grade: Optional[str] = Field(None, max_length=20, description="强度等级")
    description: Optional[str] = Field(None, description="描述")
    
    cement: float = Field(0.0, ge=0, description="水泥用量(kg/m³)")
    sand: float = Field(0.0, ge=0, description="砂用量(kg/m³)")
    gravel: float = Field(0.0, ge=0, description="石子用量(kg/m³)")
    water: float = Field(0.0, ge=0, description="水用量(kg/m³)")
    admixture: float = Field(0.0, ge=0, description="外加剂用量(kg/m³)")
    fly_ash: float = Field(0.0, ge=0, description="粉煤灰用量(kg/m³)")
    mineral_powder: float = Field(0.0, ge=0, description="矿粉用量(kg/m³)")
    
    water_cement_ratio: Optional[float] = Field(None, ge=0, description="水灰比")
    slump: Optional[float] = Field(None, ge=0, description="坍落度(mm)")
    
    status: FormulaStatus = Field(default=FormulaStatus.ACTIVE, description="状态")
    is_standard: bool = Field(default=True, description="是否标准配方")
    version: int = Field(default=1, ge=1, description="版本号")


class FormulaCreate(FormulaBase):
    pass


class FormulaUpdate(BaseModel):
    formula_name: Optional[str] = None
    concrete_type: Optional[str] = None
    strength_grade: Optional[str] = None
    description: Optional[str] = None
    
    cement: Optional[float] = None
    sand: Optional[float] = None
    gravel: Optional[float] = None
    water: Optional[float] = None
    admixture: Optional[float] = None
    fly_ash: Optional[float] = None
    mineral_powder: Optional[float] = None
    
    water_cement_ratio: Optional[float] = None
    slump: Optional[float] = None
    
    status: Optional[FormulaStatus] = None
    is_standard: Optional[bool] = None


class FormulaAdjustmentCreate(BaseModel):
    formula_id: int
    
    original_cement: Optional[float] = None
    adjusted_cement: Optional[float] = None
    original_sand: Optional[float] = None
    adjusted_sand: Optional[float] = None
    original_gravel: Optional[float] = None
    adjusted_gravel: Optional[float] = None
    original_water: Optional[float] = None
    adjusted_water: Optional[float] = None
    original_admixture: Optional[float] = None
    adjusted_admixture: Optional[float] = None
    original_fly_ash: Optional[float] = None
    adjusted_fly_ash: Optional[float] = None
    original_mineral_powder: Optional[float] = None
    adjusted_mineral_powder: Optional[float] = None
    
    adjustment_reason: Optional[str] = None
    project_name: Optional[str] = None
    project_requirements: Optional[str] = None
    adjusted_by: Optional[str] = None


class FormulaAdjustment(BaseModel):
    id: int
    formula_id: int
    
    original_cement: Optional[float]
    adjusted_cement: Optional[float]
    original_sand: Optional[float]
    adjusted_sand: Optional[float]
    original_gravel: Optional[float]
    adjusted_gravel: Optional[float]
    original_water: Optional[float]
    adjusted_water: Optional[float]
    original_admixture: Optional[float]
    adjusted_admixture: Optional[float]
    original_fly_ash: Optional[float]
    adjusted_fly_ash: Optional[float]
    original_mineral_powder: Optional[float]
    adjusted_mineral_powder: Optional[float]
    
    adjustment_reason: Optional[str]
    project_name: Optional[str]
    project_requirements: Optional[str]
    adjusted_by: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class Formula(FormulaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    updated_by: Optional[str]
    adjustments: List[FormulaAdjustment] = []

    class Config:
        orm_mode = True


class ProductionPlanBase(BaseModel):
    plan_code: str = Field(..., max_length=50, description="计划编码")
    plan_name: str = Field(..., max_length=100, description="计划名称")
    
    project_name: Optional[str] = Field(None, max_length=100, description="项目名称")
    project_location: Optional[str] = Field(None, max_length=200, description="项目地址")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    
    planned_start_date: Optional[datetime] = Field(None, description="计划开始日期")
    planned_end_date: Optional[datetime] = Field(None, description="计划结束日期")
    
    total_volume: float = Field(0.0, ge=0, description="总方量(m³)")
    priority: int = Field(1, ge=1, le=5, description="优先级(1-5)")
    status: ProductionStatus = Field(default=ProductionStatus.PENDING, description="状态")
    remarks: Optional[str] = Field(None, description="备注")


class ProductionPlanCreate(ProductionPlanBase):
    pass


class ProductionPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    project_name: Optional[str] = None
    project_location: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    total_volume: Optional[float] = None
    priority: Optional[int] = None
    status: Optional[ProductionStatus] = None
    remarks: Optional[str] = None


class ProductionOrderBase(BaseModel):
    order_code: str = Field(..., max_length=50, description="任务单编码")
    plan_id: Optional[int] = Field(None, description="所属计划ID")
    formula_id: int = Field(..., description="配方ID")
    
    batch_number: Optional[str] = Field(None, max_length=50, description="批次号")
    volume: float = Field(..., gt=0, description="生产方量(m³)")
    unit: str = Field(default="m³", max_length=10, description="单位")
    
    pouring_location: Optional[str] = Field(None, max_length=200, description="浇筑位置")
    pouring_method: Optional[str] = Field(None, max_length=50, description="浇筑方式")
    
    scheduled_time: Optional[datetime] = Field(None, description="计划时间")
    status: ProductionStatus = Field(default=ProductionStatus.PENDING, description="状态")
    current_stage: ProductionStage = Field(default=ProductionStage.BATCHING, description="当前阶段")
    remarks: Optional[str] = Field(None, description="备注")


class ProductionOrderCreate(ProductionOrderBase):
    pass


class ProductionOrderUpdate(BaseModel):
    plan_id: Optional[int] = None
    formula_id: Optional[int] = None
    batch_number: Optional[str] = None
    volume: Optional[float] = None
    pouring_location: Optional[str] = None
    pouring_method: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[ProductionStatus] = None
    current_stage: Optional[ProductionStage] = None
    progress: Optional[float] = None
    remarks: Optional[str] = None


class ResourceBase(BaseModel):
    resource_code: str = Field(..., max_length=50, description="资源编码")
    resource_name: str = Field(..., max_length=100, description="资源名称")
    resource_type: ResourceType = Field(..., description="资源类型")
    model: Optional[str] = Field(None, max_length=100, description="型号")
    capacity: Optional[float] = Field(None, ge=0, description="容量")
    capacity_unit: str = Field(default="m³", max_length=20, description="容量单位")
    license_plate: Optional[str] = Field(None, max_length=20, description="车牌号")
    manufacture_year: Optional[int] = Field(None, description="制造年份")
    status: ResourceStatus = Field(default=ResourceStatus.AVAILABLE, description="状态")
    remarks: Optional[str] = Field(None, description="备注")


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    resource_name: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    model: Optional[str] = None
    capacity: Optional[float] = None
    capacity_unit: Optional[str] = None
    license_plate: Optional[str] = None
    manufacture_year: Optional[int] = None
    status: Optional[ResourceStatus] = None
    remarks: Optional[str] = None


class ResourceAllocationBase(BaseModel):
    resource_id: int = Field(..., description="资源ID")
    plan_id: Optional[int] = Field(None, description="计划ID")
    order_id: Optional[int] = Field(None, description="任务单ID")
    allocation_start_time: Optional[datetime] = Field(None, description="分配开始时间")
    allocation_end_time: Optional[datetime] = Field(None, description="分配结束时间")
    allocated_by: Optional[str] = Field(None, max_length=50, description="分配人")
    allocation_reason: Optional[str] = Field(None, description="分配原因")


class ResourceAllocationCreate(ResourceAllocationBase):
    pass


class ProductionLogBase(BaseModel):
    order_id: int = Field(..., description="任务单ID")
    stage: Optional[ProductionStage] = Field(None, description="生产阶段")
    
    batch_weight_cement: Optional[float] = Field(None, description="水泥批次重量")
    batch_weight_sand: Optional[float] = Field(None, description="砂批次重量")
    batch_weight_gravel: Optional[float] = Field(None, description="石子批次重量")
    batch_weight_water: Optional[float] = Field(None, description="水批次重量")
    batch_weight_admixture: Optional[float] = Field(None, description="外加剂批次重量")
    batch_weight_fly_ash: Optional[float] = Field(None, description="粉煤灰批次重量")
    batch_weight_mineral_powder: Optional[float] = Field(None, description="矿粉批次重量")
    
    mixing_time: Optional[int] = Field(None, description="搅拌时间(秒)")
    mixing_speed: Optional[float] = Field(None, description="搅拌速度")
    
    discharge_volume: Optional[float] = Field(None, description="出料方量")
    discharge_duration: Optional[int] = Field(None, description="出料时长(秒)")
    
    temperature: Optional[float] = Field(None, description="环境温度")
    humidity: Optional[float] = Field(None, description="环境湿度")
    
    log_message: Optional[str] = Field(None, description="日志消息")


class ProductionLogCreate(ProductionLogBase):
    pass


class ProductionAlertBase(BaseModel):
    order_id: Optional[int] = Field(None, description="任务单ID")
    alert_code: Optional[str] = Field(None, max_length=50, description="预警编码")
    alert_title: str = Field(..., max_length=200, description="预警标题")
    alert_message: Optional[str] = Field(None, description="预警消息")
    alert_level: AlertLevel = Field(default=AlertLevel.WARNING, description="预警级别")
    alert_status: AlertStatus = Field(default=AlertStatus.OPEN, description="预警状态")
    related_stage: Optional[ProductionStage] = Field(None, description="相关阶段")


class ProductionAlertCreate(ProductionAlertBase):
    pass


class ProductionAlertUpdate(BaseModel):
    alert_status: Optional[AlertStatus] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None


class Resource(ResourceBase):
    id: int
    current_order_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ResourceAllocation(ResourceAllocationBase):
    id: int
    is_active: bool
    created_at: datetime
    resource: Optional[Resource] = None

    class Config:
        orm_mode = True


class ProductionLog(ProductionLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ProductionAlert(ProductionAlertBase):
    id: int
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class ProductionStatusHistory(BaseModel):
    id: int
    order_id: int
    previous_status: Optional[ProductionStatus]
    new_status: Optional[ProductionStatus]
    previous_stage: Optional[ProductionStage]
    new_stage: Optional[ProductionStage]
    changed_by: Optional[str]
    change_reason: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class ProductionOrder(ProductionOrderBase):
    id: int
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    progress: float
    created_at: datetime
    updated_at: Optional[datetime]
    production_logs: List[ProductionLog] = []
    production_alerts: List[ProductionAlert] = []
    status_history: List[ProductionStatusHistory] = []
    resource_allocations: List[ResourceAllocation] = []

    class Config:
        orm_mode = True


class ProductionPlan(ProductionPlanBase):
    id: int
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    completed_volume: float
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    orders: List[ProductionOrder] = []
    resource_allocations: List[ResourceAllocation] = []

    class Config:
        orm_mode = True
