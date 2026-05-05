from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class MaterialType(str, Enum):
    CEMENT = "水泥"
    SAND = "砂石"
    FLY_ASH = "粉煤灰"
    ADDITIVE = "外加剂"
    WATER = "水"

class SiloBase(BaseModel):
    name: str = Field(..., description="料仓名称")
    material_type: str = Field(..., description="物料类型")
    capacity: float = Field(..., gt=0, description="料仓最大容量(吨)")
    current_level: float = Field(default=0.0, ge=0, description="当前剩余量(吨)")
    min_threshold: float = Field(default=10.0, ge=0, description="低库存预警阈值(吨)")
    unit: str = Field(default="吨", description="计量单位")

class SiloCreate(SiloBase):
    pass

class SiloUpdate(BaseModel):
    name: Optional[str] = None
    material_type: Optional[str] = None
    capacity: Optional[float] = None
    current_level: Optional[float] = None
    min_threshold: Optional[float] = None
    status: Optional[str] = None

class SiloResponse(SiloBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class InventoryRecordBase(BaseModel):
    silo_id: int = Field(..., description="料仓ID")
    change_type: str = Field(..., description="变更类型：入库/出库/调整")
    quantity: float = Field(..., description="变更数量(吨)")
    reason: Optional[str] = Field(None, description="变更原因")
    operator: Optional[str] = Field(None, description="操作人")

class InventoryRecordCreate(InventoryRecordBase):
    pass

class InventoryRecordResponse(InventoryRecordBase):
    id: int
    balance_before: float
    balance_after: float
    record_time: datetime

    class Config:
        orm_mode = True

class ProductionPlanBase(BaseModel):
    plan_name: str = Field(..., description="生产计划名称")
    plan_date: date = Field(..., description="计划日期")
    concrete_volume: float = Field(..., gt=0, description="计划生产混凝土方量(立方米)")
    concrete_grade: Optional[str] = Field(None, description="混凝土标号")
    description: Optional[str] = Field(None, description="计划描述")

class ProductionPlanCreate(ProductionPlanBase):
    pass

class ProductionPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    plan_date: Optional[date] = None
    concrete_volume: Optional[float] = None
    concrete_grade: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None

class ProductionPlanResponse(ProductionPlanBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class MaterialDemandBase(BaseModel):
    production_plan_id: int
    material_type: str
    required_quantity: float
    unit_consumption: float
    priority: int = Field(default=1, ge=1, le=4)

class MaterialDemandCreate(MaterialDemandBase):
    pass

class MaterialDemandResponse(MaterialDemandBase):
    id: int
    current_stock: float
    shortage: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class SupplierBase(BaseModel):
    name: str = Field(..., description="供应商名称")
    contact_person: Optional[str] = Field(None, description="联系人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    address: Optional[str] = Field(None, description="地址")
    material_types: Optional[str] = Field(None, description="供应物料类型")

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    material_types: Optional[str] = None
    status: Optional[str] = None

class SupplierResponse(SupplierBase):
    id: int
    overall_rating: float
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SupplierRatingBase(BaseModel):
    supplier_id: int
    rating_date: date
    delivery_score: float = Field(..., ge=1, le=10)
    quality_score: float = Field(..., ge=1, le=10)
    price_score: float = Field(default=7.0, ge=1, le=10)
    service_score: float = Field(default=7.0, ge=1, le=10)
    comment: Optional[str] = None
    evaluator: Optional[str] = None

class SupplierRatingCreate(SupplierRatingBase):
    pass

class SupplierRatingResponse(SupplierRatingBase):
    id: int
    total_score: float
    created_at: datetime

    class Config:
        orm_mode = True

class PurchaseOrderBase(BaseModel):
    supplier_id: int
    material_type: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    order_date: date
    delivery_date: Optional[date] = None
    remark: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderUpdate(BaseModel):
    actual_delivery_date: Optional[date] = None
    status: Optional[str] = None
    remark: Optional[str] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    id: int
    order_no: str
    total_amount: float
    actual_delivery_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SettlementBase(BaseModel):
    purchase_order_id: int
    settlement_date: date
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    tax_rate: float = Field(default=0.13)
    remark: Optional[str] = None

class SettlementCreate(SettlementBase):
    pass

class SettlementUpdate(BaseModel):
    payment_status: Optional[str] = None
    paid_amount: Optional[float] = None
    remark: Optional[str] = None

class SettlementResponse(SettlementBase):
    id: int
    settlement_no: str
    material_type: str
    total_amount: float
    tax_amount: float
    total_payable: float
    payment_status: str
    paid_amount: float
    created_at: datetime

    class Config:
        orm_mode = True

class LowInventoryAlert(BaseModel):
    silo_id: int
    silo_name: str
    material_type: str
    current_level: float
    capacity: float
    min_threshold: float
    percentage: float

class DashboardStats(BaseModel):
    total_silos: int
    low_inventory_count: int
    total_production_plans: int
    pending_demands: int
    total_suppliers: int
    pending_settlements: int
