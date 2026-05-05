from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class QualityDataBase(BaseModel):
    inspection_date: date
    inspection_type: str
    material_name: str
    batch_no: Optional[str] = None
    supplier: Optional[str] = None
    total_samples: int = 0
    passed_samples: int = 0
    failed_samples: int = 0
    inspector: Optional[str] = None
    inspection_result: Optional[str] = None
    remarks: Optional[str] = None

class QualityDataCreate(QualityDataBase):
    pass

class QualityDataUpdate(BaseModel):
    inspection_date: Optional[date] = None
    inspection_type: Optional[str] = None
    material_name: Optional[str] = None
    batch_no: Optional[str] = None
    supplier: Optional[str] = None
    total_samples: Optional[int] = None
    passed_samples: Optional[int] = None
    failed_samples: Optional[int] = None
    inspector: Optional[str] = None
    inspection_result: Optional[str] = None
    remarks: Optional[str] = None

class QualityDataResponse(QualityDataBase):
    id: int
    pass_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductStrengthBase(BaseModel):
    test_date: date
    product_name: str
    batch_no: Optional[str] = None
    strength_standard: float = 0.0
    strength_actual: float = 0.0
    test_count: int = 0
    pass_count: int = 0
    tester: Optional[str] = None
    is_qualified: str = "合格"
    remarks: Optional[str] = None

class ProductStrengthCreate(ProductStrengthBase):
    pass

class ProductStrengthUpdate(BaseModel):
    test_date: Optional[date] = None
    product_name: Optional[str] = None
    batch_no: Optional[str] = None
    strength_standard: Optional[float] = None
    strength_actual: Optional[float] = None
    test_count: Optional[int] = None
    pass_count: Optional[int] = None
    tester: Optional[str] = None
    is_qualified: Optional[str] = None
    remarks: Optional[str] = None

class ProductStrengthResponse(ProductStrengthBase):
    id: int
    pass_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QualityTrendItem(BaseModel):
    date: str
    pass_rate: float
    material_name: Optional[str] = None
    total_samples: int
    passed_samples: int

class QualityTrendResponse(BaseModel):
    period: str
    avg_pass_rate: float
    total_samples: int
    total_passed: int
    data: List[QualityTrendItem]

class StrengthTrendItem(BaseModel):
    date: str
    avg_actual_strength: float
    standard_strength: float
    pass_rate: float
    product_name: str

class StrengthTrendResponse(BaseModel):
    period: str
    avg_pass_rate: float
    avg_strength_ratio: float
    data: List[StrengthTrendItem]
