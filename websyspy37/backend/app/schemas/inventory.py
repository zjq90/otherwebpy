"""
库存模块Pydantic schemas
用于API的数据验证和序列化
"""
from pydantic import BaseModel, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime, date
from app.validators import is_valid_phone


# 仓库相关schemas
class WarehouseBase(BaseModel):
    """
    仓库基础schema
    """
    warehouse_no: str
    name: str
    location: Optional[str] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None

    @field_validator('warehouse_no')
    @classmethod
    def validate_warehouse_no(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('仓库编码不能为空')
        v = v.strip()
        if len(v) > 50:
            raise ValueError('仓库编码长度不能超过50个字符')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError('仓库名称不能为空')
        v = v.strip()
        if len(v) > 100:
            raise ValueError('仓库名称长度不能超过100个字符')
        return v

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('位置描述长度不能超过200个字符')
        return v

    @field_validator('manager')
    @classmethod
    def validate_manager(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 50:
            raise ValueError('负责人姓名长度不能超过50个字符')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
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


class WarehouseCreate(WarehouseBase):
    """
    仓库创建schema
    """
    pass


class WarehouseUpdate(BaseModel):
    """
    仓库更新schema
    """
    warehouse_no: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip().replace('-', '').replace(' ', '')
        if not is_valid_phone(v):
            raise ValueError('手机号格式不正确，请输入11位中国大陆手机号')
        return v


class WarehouseResponse(WarehouseBase):
    """
    仓库响应schema
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 库存相关schemas
class InventoryBase(BaseModel):
    """
    库存基础schema
    """
    warehouse_id: int
    product_id: int
    quantity: int = 0
    min_quantity: int = 0
    max_quantity: int = 10000

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            return 0
        if v < 0:
            raise ValueError('库存数量不能为负数')
        if v > 10000000:
            raise ValueError('库存数量不能超过10000000')
        return v

    @field_validator('min_quantity')
    @classmethod
    def validate_min_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            return 0
        if v < 0:
            raise ValueError('最小库存不能为负数')
        if v > 10000000:
            raise ValueError('最小库存不能超过10000000')
        return v

    @field_validator('max_quantity')
    @classmethod
    def validate_max_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            return 10000
        if v < 0:
            raise ValueError('最大库存不能为负数')
        if v > 100000000:
            raise ValueError('最大库存不能超过100000000')
        return v


class InventoryCreate(InventoryBase):
    """
    库存创建schema
    """
    pass


class InventoryUpdate(BaseModel):
    """
    库存更新schema
    """
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    max_quantity: Optional[int] = None

    @field_validator('quantity')
    @classmethod
    def validate_quantity_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('库存数量不能为负数')
        if v > 10000000:
            raise ValueError('库存数量不能超过10000000')
        return v

    @field_validator('min_quantity')
    @classmethod
    def validate_min_quantity_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('最小库存不能为负数')
        if v > 10000000:
            raise ValueError('最小库存不能超过10000000')
        return v

    @field_validator('max_quantity')
    @classmethod
    def validate_max_quantity_update(cls, v: Optional[int], info: ValidationInfo) -> Optional[int]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('最大库存不能为负数')
        if v > 100000000:
            raise ValueError('最大库存不能超过100000000')
        return v


class InventoryResponse(InventoryBase):
    """
    库存响应schema
    """
    id: int
    last_updated: datetime
    created_at: datetime
    warehouse: Optional[WarehouseResponse] = None
    product: Optional[BaseModel] = None

    class Config:
        from_attributes = True


# 入库明细相关schemas
class StockInItemBase(BaseModel):
    """
    入库明细基础schema
    """
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('数量不能为空')
        if v < 1:
            raise ValueError('数量必须大于0')
        if v > 1000000:
            raise ValueError('数量不能超过1000000')
        return v

    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('单价不能为空')
        if v < 0:
            raise ValueError('单价不能为负数')
        if v > 1000000000:
            raise ValueError('单价不能超过1000000000')
        return round(v, 2)

    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('总价不能为空')
        if v < 0:
            raise ValueError('总价不能为负数')
        if v > 10000000000:
            raise ValueError('总价不能超过10000000000')
        return round(v, 2)


class StockInItemCreate(StockInItemBase):
    """
    入库明细创建schema
    """
    pass


class StockInItemResponse(StockInItemBase):
    """
    入库明细响应schema
    """
    id: int
    stock_in_order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 入库单相关schemas
class StockInOrderBase(BaseModel):
    """
    入库单基础schema
    """
    warehouse_id: int
    supplier: Optional[str] = None
    total_amount: float = 0.0
    status: str = "待入库"
    remark: Optional[str] = None

    @field_validator('supplier')
    @classmethod
    def validate_supplier(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('供应商名称长度不能超过200个字符')
        return v

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('金额不能为负数')
        if v > 100000000000:
            raise ValueError('金额不能超过100000000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待入库"
        v = v.strip()
        valid_statuses = ["待入库", "已入库", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('remark')
    @classmethod
    def validate_remark(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('备注长度不能超过500个字符')
        return v


class StockInOrderCreate(StockInOrderBase):
    """
    入库单创建schema
    """
    stock_in_items: List[StockInItemCreate] = []


class StockInOrderUpdate(BaseModel):
    """
    入库单更新schema
    """
    warehouse_id: Optional[int] = None
    supplier: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    remark: Optional[str] = None

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('金额不能为负数')
        if v > 100000000000:
            raise ValueError('金额不能超过100000000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待入库", "已入库", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class StockInOrderResponse(StockInOrderBase):
    """
    入库单响应schema
    """
    id: int
    order_no: str
    order_date: datetime
    created_at: datetime
    updated_at: datetime
    stock_in_items: List[StockInItemResponse] = []
    warehouse: Optional[WarehouseResponse] = None

    class Config:
        from_attributes = True


# 出库明细相关schemas
class StockOutItemBase(BaseModel):
    """
    出库明细基础schema
    """
    product_id: int
    quantity: int
    unit_price: float
    total_price: float

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int, info: ValidationInfo) -> int:
        if v is None:
            raise ValueError('数量不能为空')
        if v < 1:
            raise ValueError('数量必须大于0')
        if v > 1000000:
            raise ValueError('数量不能超过1000000')
        return v

    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('单价不能为空')
        if v < 0:
            raise ValueError('单价不能为负数')
        if v > 1000000000:
            raise ValueError('单价不能超过1000000000')
        return round(v, 2)

    @field_validator('total_price')
    @classmethod
    def validate_total_price(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            raise ValueError('总价不能为空')
        if v < 0:
            raise ValueError('总价不能为负数')
        if v > 10000000000:
            raise ValueError('总价不能超过10000000000')
        return round(v, 2)


class StockOutItemCreate(StockOutItemBase):
    """
    出库明细创建schema
    """
    pass


class StockOutItemResponse(StockOutItemBase):
    """
    出库明细响应schema
    """
    id: int
    stock_out_order_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 出库单相关schemas
class StockOutOrderBase(BaseModel):
    """
    出库单基础schema
    """
    warehouse_id: int
    customer: Optional[str] = None
    total_amount: float = 0.0
    status: str = "待出库"
    remark: Optional[str] = None

    @field_validator('customer')
    @classmethod
    def validate_customer(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError('客户名称长度不能超过200个字符')
        return v

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount(cls, v: float, info: ValidationInfo) -> float:
        if v is None:
            return 0.0
        if v < 0:
            raise ValueError('金额不能为负数')
        if v > 100000000000:
            raise ValueError('金额不能超过100000000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        if v is None:
            return "待出库"
        v = v.strip()
        valid_statuses = ["待出库", "已出库", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一：{", ".join(valid_statuses)}')
        return v

    @field_validator('remark')
    @classmethod
    def validate_remark(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None or v == '':
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('备注长度不能超过500个字符')
        return v


class StockOutOrderCreate(StockOutOrderBase):
    """
    出库单创建schema
    """
    stock_out_items: List[StockOutItemCreate] = []


class StockOutOrderUpdate(BaseModel):
    """
    出库单更新schema
    """
    warehouse_id: Optional[int] = None
    customer: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    remark: Optional[str] = None

    @field_validator('total_amount')
    @classmethod
    def validate_total_amount_update(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError('金额不能为负数')
        if v > 100000000000:
            raise ValueError('金额不能超过100000000000')
        return round(v, 2)

    @field_validator('status')
    @classmethod
    def validate_status_update(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        valid_statuses = ["待出库", "已出库", "已取消"]
        if v not in valid_statuses:
            raise ValueError(f'状态必须是以下之一：{", ".join(valid_statuses)}')
        return v


class StockOutOrderResponse(StockOutOrderBase):
    """
    出库单响应schema
    """
    id: int
    order_no: str
    order_date: datetime
    created_at: datetime
    updated_at: datetime
    stock_out_items: List[StockOutItemResponse] = []
    warehouse: Optional[WarehouseResponse] = None

    class Config:
        from_attributes = True
