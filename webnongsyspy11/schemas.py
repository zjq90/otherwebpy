"""
Pydantic模型定义
用于API请求验证和响应序列化
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Generic, TypeVar
from datetime import date, datetime
import math
import re

T = TypeVar('T')


class PageParams(BaseModel):
    """分页参数模型"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=10, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def create_paginated_response(items: List[T], total: int, page: int, page_size: int) -> PaginatedResponse[T]:
    """创建分页响应"""
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


class SupplierBase(BaseModel):
    """供应商基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v:
            v = v.strip()
            if not re.match(r'^1[3-9]\d{9}$|^0\d{2,3}-?\d{7,8}$', v):
                raise ValueError('电话号码格式不正确，请输入有效的手机号码或固定电话号码')
        return v


class SupplierCreate(SupplierBase):
    """创建供应商模型"""
    pass


class SupplierUpdate(SupplierBase):
    """更新供应商模型"""
    pass


class Supplier(SupplierBase):
    """供应商响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    code: str = Field(..., min_length=1, max_length=20, description="分类编码")
    description: Optional[str] = Field(None, max_length=200, description="分类描述")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if v:
            v = v.strip().upper()
            if not re.match(r'^[A-Z0-9_]+$', v):
                raise ValueError('分类编码只能包含大写字母、数字和下划线')
        return v


class CategoryCreate(CategoryBase):
    """创建分类模型"""
    pass


class CategoryUpdate(CategoryBase):
    """更新分类模型"""
    pass


class Category(CategoryBase):
    """分类响应模型"""
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SupplyBase(BaseModel):
    """农资基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="农资名称")
    category_id: int = Field(..., gt=0, description="分类ID")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    specification: Optional[str] = Field(None, max_length=100, description="规格")
    brand: Optional[str] = Field(None, max_length=50, description="品牌")
    warning_threshold: float = Field(default=10.0, ge=0, le=1000000, description="库存预警阈值")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class SupplyCreate(SupplyBase):
    """创建农资模型"""
    pass


class SupplyUpdate(SupplyBase):
    """更新农资模型"""
    pass


class Supply(SupplyBase):
    """农资响应模型"""
    id: int
    category: Optional[Category] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PlotBase(BaseModel):
    """地块基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="地块名称")
    location: Optional[str] = Field(None, max_length=200, description="位置")
    area: Optional[float] = Field(None, ge=0, le=1000000, description="面积（亩）")
    soil_type: Optional[str] = Field(None, max_length=50, description="土壤类型")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class PlotCreate(PlotBase):
    """创建地块模型"""
    pass


class PlotUpdate(PlotBase):
    """更新地块模型"""
    pass


class Plot(PlotBase):
    """地块响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CropBase(BaseModel):
    """作物基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="作物名称")
    variety: Optional[str] = Field(None, max_length=100, description="品种")
    growth_cycle: Optional[int] = Field(None, ge=1, le=1000, description="生长周期（天）")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class CropCreate(CropBase):
    """创建作物模型"""
    pass


class CropUpdate(CropBase):
    """更新作物模型"""
    pass


class Crop(CropBase):
    """作物响应模型"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    """采购基础模型"""
    supplier_id: int = Field(..., gt=0, description="供应商ID")
    supply_id: int = Field(..., gt=0, description="农资ID")
    purchase_date: date = Field(..., description="采购日期")
    quantity: float = Field(..., gt=0, le=1000000, description="采购数量")
    unit_price: float = Field(..., gt=0, le=1000000, description="单价")
    batch_no: str = Field(..., min_length=1, max_length=50, description="批次号")
    expiry_date: Optional[date] = Field(None, description="保质期")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator('purchase_date')
    @classmethod
    def validate_purchase_date(cls, v):
        if v > date.today():
            raise ValueError('采购日期不能晚于今天')
        return v

    @field_validator('expiry_date')
    @classmethod
    def validate_expiry_date(cls, v, info):
        if v and 'purchase_date' in info.data and v < info.data['purchase_date']:
            raise ValueError('保质期不能早于采购日期')
        return v


class PurchaseCreate(PurchaseBase):
    """创建采购模型"""
    pass


class PurchaseUpdate(PurchaseBase):
    """更新采购模型"""
    pass


class Purchase(PurchaseBase):
    """采购响应模型"""
    id: int
    purchase_no: str
    total_price: Optional[float] = None
    supplier: Optional[Supplier] = None
    supply: Optional[Supply] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    """库存基础模型"""
    supply_id: int = Field(..., gt=0, description="农资ID")
    purchase_id: int = Field(..., gt=0, description="采购ID")
    batch_no: str = Field(..., min_length=1, max_length=50, description="批次号")
    quantity: float = Field(default=0, ge=0, le=1000000, description="库存数量")
    expiry_date: Optional[date] = Field(None, description="保质期")
    is_expired: bool = Field(default=False, description="是否过期")


class InventoryCreate(InventoryBase):
    """创建库存模型"""
    pass


class InventoryUpdate(BaseModel):
    """更新库存模型"""
    quantity: Optional[float] = Field(None, ge=0, le=1000000, description="库存数量")
    is_expired: Optional[bool] = Field(None, description="是否过期")


class Inventory(InventoryBase):
    """库存响应模型"""
    id: int
    supply: Optional[Supply] = None
    purchase: Optional[Purchase] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UsageRecordBase(BaseModel):
    """使用记录基础模型"""
    usage_date: date = Field(..., description="使用日期")
    supply_id: int = Field(..., gt=0, description="农资ID")
    inventory_id: int = Field(..., gt=0, description="库存ID")
    plot_id: int = Field(..., gt=0, description="地块ID")
    crop_id: int = Field(..., gt=0, description="作物ID")
    quantity: float = Field(..., gt=0, le=1000000, description="使用数量")
    usage_method: Optional[str] = Field(None, max_length=100, description="使用方法")
    operator: Optional[str] = Field(None, max_length=50, description="操作人")
    remark: Optional[str] = Field(None, max_length=500, description="备注")

    @field_validator('usage_date')
    @classmethod
    def validate_usage_date(cls, v):
        if v > date.today():
            raise ValueError('使用日期不能晚于今天')
        return v


class UsageRecordCreate(UsageRecordBase):
    """创建使用记录模型"""
    pass


class UsageRecordUpdate(UsageRecordBase):
    """更新使用记录模型"""
    pass


class UsageRecord(UsageRecordBase):
    """使用记录响应模型"""
    id: int
    supply: Optional[Supply] = None
    inventory: Optional[Inventory] = None
    plot: Optional[Plot] = None
    crop: Optional[Crop] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InventorySummary(BaseModel):
    """库存汇总模型"""
    supply_id: int
    supply_name: str
    category_name: str
    total_quantity: float
    unit: str
    warning_threshold: float
    is_below_threshold: bool


class AlertItem(BaseModel):
    """预警项模型"""
    supply_id: int
    supply_name: str
    category_name: str
    current_quantity: float
    warning_threshold: float
    alert_type: str
