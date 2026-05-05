"""
生产模块Pydantic schemas
用于API的数据验证和序列化
"""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime, date


# 产品相关schemas
class ProductBase(BaseModel):
    """
    产品基础schema
    """
    product_no: str
    name: str
    specification: Optional[str] = None
    unit: str = "个"
    cost_price: float = 0.0
    selling_price: float = 0.0
    description: Optional[str] = None

    @field_validator('product_no')
    @classmethod
    def validate_product_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('产品编码不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('产品编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('产品名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('产品名称长度不能超过100个字符')
        return v

    @field_validator('specification')
    @classmethod
    def validate_specification(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('规格描述长度不能超过200个字符')
        return v

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v: str, info: ValidationInfo) -> str:
        if v is None or v == '':
            return "个"
        v = v.strip()
        if len(v) > 20:
            raise ValueError('单位长度不能超过20个字符')
        return v

    @field_validator('cost_price')
    @classmethod
    def validate_cost_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('成本价格不能为负数')
        if v > 1000000000:
            raise ValueError('成本价格不能超过1000000000')
        return round(v, 2)

    @field_validator('selling_price')
    @classmethod
    def validate_selling_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('销售价格不能为负数')
        if v > 1000000000:
            raise ValueError('销售价格不能超过1000000000')
        return round(v, 2)

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class ProductCreate(ProductBase):
    """
    产品创建schema
    """
    pass


class ProductUpdate(BaseModel):
    """
    产品更新schema
    """
    product_no: Optional[str] = None
    name: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    description: Optional[str] = None

    @field_validator('cost_price')
    @classmethod
    def validate_cost_price_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('成本价格不能为负数')
        if v > 1000000000:
            raise ValueError('成本价格不能超过1000000000')
        return round(v, 2)

    @field_validator('selling_price')
    @classmethod
    def validate_selling_price_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('销售价格不能为负数')
        if v > 1000000000:
            raise ValueError('销售价格不能超过1000000000')
        return round(v, 2)


class ProductResponse(ProductBase):
    """
    产品响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 生产任务相关schemas
class ProductionTaskBase(BaseModel):
    """
    生产任务基础schema
    """
    plan_id: Optional[int] = None
    product_id: int
    quantity: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_quantity: int = 0
    status: str = "待处理"
    description: Optional[str] = None

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('生产数量不能为空')
        if v < 1:
            raise ValueError('生产数量必须大于0')
        if v > 1000000:
            raise ValueError('生产数量不能超过1000000')
        return v

    @field_validator('actual_quantity')
    @classmethod
    def validate_actual_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            return 0
        if v < 0:
            raise ValueError('实际生产数量不能为负数')
        if v > 1000000:
            raise ValueError('实际生产数量不能超过1000000')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待处理"
        v = v.strip()
        valid_statuses = ["待处理", "生产中", "已完成", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'任务状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class ProductionTaskCreate(ProductionTaskBase):
    """
    生产任务创建schema
    """
    task_no: Optional[str] = None


class ProductionTaskUpdate(BaseModel):
    """
    生产任务更新schema
    """
    plan_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_quantity: Optional[int] = None
    status: Optional[str] = None
    description: Optional[str] = None

    @field_validator('quantity')
    @classmethod
    def validate_quantity_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 1:
            raise ValueError('生产数量必须大于0')
        if v > 1000000:
            raise ValueError('生产数量不能超过1000000')
        return v

    @field_validator('actual_quantity')
    @classmethod
    def validate_actual_quantity_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('实际生产数量不能为负数')
        if v > 1000000:
            raise ValueError('实际生产数量不能超过1000000')
        return v

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待处理", "生产中", "已完成", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'任务状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class ProductionTaskResponse(ProductionTaskBase):
    """
    生产任务响应schema
    """
    id: int
    task_no: str
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# 生产计划相关schemas
class ProductionPlanBase(BaseModel):
    """
    生产计划基础schema
    """
    plan_no: str
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "待执行"
    description: Optional[str] = None

    @field_validator('plan_no')
    @classmethod
    def validate_plan_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('计划编码不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('计划编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('计划名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('计划名称长度不能超过100个字符')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待执行"
        v = v.strip()
        valid_statuses = ["待执行", "执行中", "已完成", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'计划状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('描述长度不能超过500个字符')
        return v


class ProductionPlanCreate(ProductionPlanBase):
    """
    生产计划创建schema
    """
    pass


class ProductionPlanUpdate(BaseModel):
    """
    生产计划更新schema
    """
    plan_no: Optional[str] = None
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    description: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待执行", "执行中", "已完成", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'计划状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class ProductionPlanResponse(ProductionPlanBase):
    """
    生产计划响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime
    production_tasks: List[ProductionTaskResponse] = []

    class Config:
        from_attributes = True
