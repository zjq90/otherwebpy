"""
Pydantic数据模型定义
用于API请求参数验证和响应数据序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: str = Field(..., max_length=50, description="真实姓名")
    role: str = Field(..., description="角色：管理员/采购员")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    real_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    is_active: Optional[int] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应模型"""
    token: str
    user: UserResponse


class SupplierBase(BaseModel):
    """供应商基础模型"""
    supplier_name: str = Field(..., max_length=100, description="供应商名称")
    contact_person: Optional[str] = Field(None, max_length=50, description="联系人")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    business_license: Optional[str] = Field(None, max_length=100, description="营业执照号")
    description: Optional[str] = Field(None, description="供应商描述")


class SupplierCreate(SupplierBase):
    """供应商创建模型"""
    pass


class SupplierUpdate(BaseModel):
    """供应商更新模型"""
    supplier_name: Optional[str] = Field(None, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=200)
    business_license: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[int] = None


class SupplierResponse(SupplierBase):
    """供应商响应模型"""
    id: int
    quality_rating: float
    total_orders: int
    total_amount: float
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaterialBase(BaseModel):
    """原材料基础模型"""
    material_name: str = Field(..., max_length=100, description="原材料名称")
    material_type: str = Field(..., description="类型：水泥/砂石/粉煤灰/外加剂")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: str = Field(default="吨", max_length=20, description="计量单位")
    description: Optional[str] = Field(None, description="描述")


class MaterialCreate(MaterialBase):
    """原材料创建模型"""
    pass


class MaterialUpdate(BaseModel):
    """原材料更新模型"""
    material_name: Optional[str] = Field(None, max_length=100)
    material_type: Optional[str] = None
    specification: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None


class MaterialResponse(MaterialBase):
    """原材料响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WarehouseBase(BaseModel):
    """料仓基础模型"""
    warehouse_name: str = Field(..., max_length=100, description="料仓名称")
    location: Optional[str] = Field(None, max_length=200, description="位置")
    max_capacity: float = Field(..., gt=0, description="最大容量")
    description: Optional[str] = Field(None, description="描述")


class WarehouseCreate(WarehouseBase):
    """料仓创建模型"""
    pass


class WarehouseUpdate(BaseModel):
    """料仓更新模型"""
    warehouse_name: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    max_capacity: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    is_active: Optional[int] = None


class WarehouseResponse(WarehouseBase):
    """料仓响应模型"""
    id: int
    current_usage: float
    is_active: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryBase(BaseModel):
    """库存基础模型"""
    material_id: int = Field(..., description="原材料ID")
    warehouse_id: int = Field(..., description="料仓ID")
    quantity: float = Field(default=0, ge=0, description="当前库存数量")
    safety_threshold: float = Field(default=100, gt=0, description="安全阈值")
    unit_price: Optional[float] = Field(None, gt=0, description="单价")
    production_date: Optional[datetime] = Field(None, description="生产日期")
    expiry_date: Optional[datetime] = Field(None, description="保质期/到期日期")
    batch_number: Optional[str] = Field(None, max_length=100, description="批次号")


class InventoryCreate(InventoryBase):
    """库存创建模型"""
    pass


class InventoryUpdate(BaseModel):
    """库存更新模型"""
    quantity: Optional[float] = Field(None, ge=0)
    safety_threshold: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, gt=0)
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    batch_number: Optional[str] = Field(None, max_length=100)


class InventoryDetailResponse(BaseModel):
    """库存详情响应模型（包含关联信息）"""
    id: int
    material_id: int
    warehouse_id: int
    material_name: str
    material_type: str
    specification: Optional[str]
    warehouse_name: str
    warehouse_location: Optional[str]
    quantity: float
    unit: str
    safety_threshold: float
    unit_price: Optional[float]
    production_date: Optional[datetime]
    expiry_date: Optional[datetime]
    batch_number: Optional[str]
    is_low_stock: int
    last_check_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PurchaseRequestBase(BaseModel):
    """采购申请基础模型"""
    material_id: int = Field(..., description="原材料ID")
    quantity: float = Field(..., gt=0, description="需求数量")
    unit: str = Field(default="吨", max_length=20, description="单位")
    expected_delivery_date: Optional[datetime] = Field(None, description="预计到货时间")
    reason: Optional[str] = Field(None, description="申请原因")


class PurchaseRequestCreate(PurchaseRequestBase):
    """采购申请创建模型"""
    pass


class PurchaseRequestUpdate(BaseModel):
    """采购申请更新模型"""
    quantity: Optional[float] = Field(None, gt=0)
    expected_delivery_date: Optional[datetime] = None
    reason: Optional[str] = None


class PurchaseApproval(BaseModel):
    """采购审批模型"""
    status: str = Field(..., description="审批状态：已批准/已拒绝")
    approval_comment: Optional[str] = Field(None, description="审批意见")


class PurchaseRequestDetailResponse(BaseModel):
    """采购申请详情响应模型"""
    id: int
    request_no: str
    material_id: int
    material_name: str
    material_type: str
    requested_by: int
    requester_name: str
    quantity: float
    unit: str
    expected_delivery_date: Optional[datetime]
    status: str
    reason: Optional[str]
    approved_by: Optional[int]
    approver_name: Optional[str]
    approval_time: Optional[datetime]
    approval_comment: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupplyRecordBase(BaseModel):
    """供货记录基础模型"""
    supplier_id: int = Field(..., description="供应商ID")
    material_id: int = Field(..., description="原材料ID")
    quantity: float = Field(..., gt=0, description="供货数量")
    unit_price: float = Field(..., gt=0, description="单价")
    delivery_date: Optional[datetime] = Field(None, description="送货日期")
    quality_status: str = Field(default="合格", description="质量状态")
    batch_number: Optional[str] = Field(None, max_length=100, description="批次号")
    remark: Optional[str] = Field(None, description="备注")


class SupplyRecordCreate(SupplyRecordBase):
    """供货记录创建模型"""
    pass


class SupplyRecordResponse(BaseModel):
    """供货记录响应模型"""
    id: int
    supplier_id: int
    supplier_name: str
    material_id: int
    material_name: str
    material_type: str
    quantity: float
    unit: str
    unit_price: float
    total_amount: float
    delivery_date: Optional[datetime]
    quality_status: str
    batch_number: Optional[str]
    remark: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierEvaluationBase(BaseModel):
    """供应商评价基础模型"""
    supplier_id: int = Field(..., description="供应商ID")
    quality_score: float = Field(default=5.0, ge=1, le=5, description="质量评分")
    delivery_score: float = Field(default=5.0, ge=1, le=5, description="交货及时性评分")
    price_score: float = Field(default=5.0, ge=1, le=5, description="价格合理性评分")
    service_score: float = Field(default=5.0, ge=1, le=5, description="服务态度评分")
    comment: Optional[str] = Field(None, description="评价内容")


class SupplierEvaluationCreate(SupplierEvaluationBase):
    """供应商评价创建模型"""
    pass


class SupplierEvaluationResponse(BaseModel):
    """供应商评价响应模型"""
    id: int
    supplier_id: int
    supplier_name: str
    evaluated_by: int
    evaluator_name: str
    quality_score: float
    delivery_score: float
    price_score: float
    service_score: float
    total_score: float
    comment: Optional[str]
    evaluation_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class StockAlertResponse(BaseModel):
    """库存预警响应模型"""
    id: int
    inventory_id: int
    material_name: str
    material_type: str
    warehouse_name: str
    alert_type: str
    threshold_value: float
    current_value: float
    message: str
    is_read: int
    is_handled: int
    handled_by: Optional[int]
    handled_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """仪表盘统计数据模型"""
    total_materials: int
    total_inventory_value: float
    low_stock_count: int
    pending_purchase_requests: int
    total_suppliers: int
    avg_supplier_rating: float


class APIResponse(BaseModel):
    """通用API响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class PaginationResponse(BaseModel):
    """分页响应模型"""
    success: bool = True
    message: str = "获取成功"
    data: dict = {}
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
