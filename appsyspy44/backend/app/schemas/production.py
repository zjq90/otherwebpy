from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class ProductionDataBase(BaseModel):
    production_date: date
    shift: str
    product_name: str
    planned_quantity: int = 0
    actual_quantity: int = 0
    qualified_quantity: int = 0
    work_hours: float = 0.0
    operator: Optional[str] = None
    remarks: Optional[str] = None

class ProductionDataCreate(ProductionDataBase):
    pass

class ProductionDataUpdate(BaseModel):
    production_date: Optional[date] = None
    shift: Optional[str] = None
    product_name: Optional[str] = None
    planned_quantity: Optional[int] = None
    actual_quantity: Optional[int] = None
    qualified_quantity: Optional[int] = None
    work_hours: Optional[float] = None
    operator: Optional[str] = None
    remarks: Optional[str] = None

class ProductionDataResponse(ProductionDataBase):
    id: int
    completion_rate: float
    pass_rate: float
    efficiency: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductionTaskBase(BaseModel):
    task_no: str
    product_name: str
    planned_quantity: int = 0
    start_date: date
    end_date: date
    priority: int = 1
    status: str = "pending"
    assigned_to: Optional[str] = None
    description: Optional[str] = None

class ProductionTaskCreate(ProductionTaskBase):
    pass

class ProductionTaskUpdate(BaseModel):
    task_no: Optional[str] = None
    product_name: Optional[str] = None
    planned_quantity: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    description: Optional[str] = None

class ProductionTaskResponse(ProductionTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductionReportItem(BaseModel):
    date: str
    actual_quantity: int
    planned_quantity: int
    completion_rate: float
    qualified_quantity: int
    pass_rate: float
    product_name: Optional[str] = None

class ProductionReportResponse(BaseModel):
    period: str
    total_planned: int
    total_actual: int
    total_qualified: int
    avg_completion_rate: float
    avg_pass_rate: float
    data: List[ProductionReportItem]

class ChartDataItem(BaseModel):
    name: str
    value: float

from app.schemas.common import ChartResponse
