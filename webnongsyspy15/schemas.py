"""
Pydantic模型定义
用于API请求和响应的数据验证
"""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ============= 用户相关模型 =============
class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    role: str = Field(default="user", description="角色")


class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """
    用户更新模型
    """
    real_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    用户登录模型
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """
    令牌模型
    """
    access_token: str
    token_type: str = "bearer"


# ============= 作物相关模型 =============
class CropBase(BaseModel):
    """
    作物基础模型
    """
    name: str = Field(..., min_length=1, max_length=100, description="作物名称")
    variety: Optional[str] = Field(None, max_length=100, description="品种")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    unit: str = Field(default="公斤", max_length=20, description="计量单位")
    growth_cycle: Optional[int] = Field(None, description="生长周期（天）")
    description: Optional[str] = Field(None, description="描述")


class CropCreate(CropBase):
    """
    作物创建模型
    """
    pass


class CropUpdate(BaseModel):
    """
    作物更新模型
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    variety: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = Field(None, max_length=20)
    growth_cycle: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CropResponse(CropBase):
    """
    作物响应模型
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= 地块相关模型 =============
class PlotBase(BaseModel):
    """
    地块基础模型
    """
    name: str = Field(..., min_length=1, max_length=100, description="地块名称")
    code: str = Field(..., min_length=1, max_length=50, description="地块编号")
    area: float = Field(..., gt=0, description="面积（亩）")
    location: Optional[str] = Field(None, max_length=255, description="位置")
    soil_type: Optional[str] = Field(None, max_length=50, description="土壤类型")
    irrigation_type: Optional[str] = Field(None, max_length=50, description="灌溉方式")
    description: Optional[str] = Field(None, description="描述")


class PlotCreate(PlotBase):
    """
    地块创建模型
    """
    pass


class PlotUpdate(BaseModel):
    """
    地块更新模型
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    area: Optional[float] = Field(None, gt=0)
    location: Optional[str] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PlotResponse(PlotBase):
    """
    地块响应模型
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= 生产记录相关模型 =============
class ProductionRecordBase(BaseModel):
    """
    生产记录基础模型
    """
    crop_id: int = Field(..., description="作物ID")
    plot_id: int = Field(..., description="地块ID")
    planting_date: date = Field(..., description="种植日期")
    harvest_date: Optional[date] = Field(None, description="收获日期")
    season: Optional[str] = Field(None, max_length=20, description="季节")
    year: int = Field(..., description="年份")
    yield_amount: float = Field(default=0.0, ge=0, description="产量")
    yield_unit: str = Field(default="公斤", max_length=20, description="产量单位")
    input_cost: float = Field(default=0.0, ge=0, description="投入成本")
    input_details: Optional[str] = Field(None, description="投入明细")
    selling_price: float = Field(default=0.0, ge=0, description="销售单价")
    revenue: float = Field(default=0.0, ge=0, description="收入")
    profit: float = Field(default=0.0, description="利润")
    notes: Optional[str] = Field(None, description="备注")


class ProductionRecordCreate(ProductionRecordBase):
    """
    生产记录创建模型
    """
    pass


class ProductionRecordUpdate(BaseModel):
    """
    生产记录更新模型
    """
    crop_id: Optional[int] = None
    plot_id: Optional[int] = None
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    season: Optional[str] = None
    year: Optional[int] = None
    yield_amount: Optional[float] = Field(None, ge=0)
    yield_unit: Optional[str] = None
    input_cost: Optional[float] = Field(None, ge=0)
    input_details: Optional[str] = None
    selling_price: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)
    profit: Optional[float] = None
    notes: Optional[str] = None


class ProductionRecordResponse(ProductionRecordBase):
    """
    生产记录响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    crop: Optional[CropResponse] = None
    plot: Optional[PlotResponse] = None

    class Config:
        from_attributes = True


# ============= 财务记录相关模型 =============
class FinancialRecordBase(BaseModel):
    """
    财务记录基础模型
    """
    record_date: date = Field(..., description="记录日期")
    record_type: str = Field(..., max_length=20, description="类型：income/expense")
    category: str = Field(..., max_length=50, description="分类")
    amount: float = Field(..., gt=0, description="金额")
    currency: str = Field(default="CNY", max_length=10, description="货币")
    description: Optional[str] = Field(None, max_length=255, description="描述")
    payment_method: Optional[str] = Field(None, max_length=50, description="支付方式")
    production_record_id: Optional[int] = Field(None, description="关联生产记录ID")
    notes: Optional[str] = Field(None, description="备注")


class FinancialRecordCreate(FinancialRecordBase):
    """
    财务记录创建模型
    """
    pass


class FinancialRecordUpdate(BaseModel):
    """
    财务记录更新模型
    """
    record_date: Optional[date] = None
    record_type: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    production_record_id: Optional[int] = None
    notes: Optional[str] = None


class FinancialRecordResponse(FinancialRecordBase):
    """
    财务记录响应模型
    """
    id: int
    year: int
    month: int
    quarter: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============= 环境记录相关模型 =============
class EnvironmentRecordBase(BaseModel):
    """
    环境记录基础模型
    """
    plot_id: int = Field(..., description="地块ID")
    record_date: date = Field(..., description="记录日期")
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")

    # 水资源
    water_usage: float = Field(default=0.0, ge=0, description="用水量（立方米）")
    water_source: Optional[str] = Field(None, max_length=50, description="水源")
    water_cost: float = Field(default=0.0, ge=0, description="用水成本")

    # 能源
    electricity_usage: float = Field(default=0.0, ge=0, description="用电量（度）")
    electricity_cost: float = Field(default=0.0, ge=0, description="用电成本")
    fuel_usage: float = Field(default=0.0, ge=0, description="燃料使用（升）")
    fuel_type: Optional[str] = Field(None, max_length=50, description="燃料类型")
    fuel_cost: float = Field(default=0.0, ge=0, description="燃料成本")

    # 农资
    fertilizer_usage: float = Field(default=0.0, ge=0, description="化肥使用量（公斤）")
    fertilizer_type: Optional[str] = Field(None, max_length=100, description="化肥类型")
    fertilizer_cost: float = Field(default=0.0, ge=0, description="化肥成本")
    pesticide_usage: float = Field(default=0.0, ge=0, description="农药使用量（公斤）")
    pesticide_type: Optional[str] = Field(None, max_length=100, description="农药类型")
    pesticide_cost: float = Field(default=0.0, ge=0, description="农药成本")
    seed_usage: float = Field(default=0.0, ge=0, description="种子使用量（公斤）")
    seed_type: Optional[str] = Field(None, max_length=100, description="种子类型")
    seed_cost: float = Field(default=0.0, ge=0, description="种子成本")

    notes: Optional[str] = Field(None, description="备注")


class EnvironmentRecordCreate(EnvironmentRecordBase):
    """
    环境记录创建模型
    """
    pass


class EnvironmentRecordUpdate(BaseModel):
    """
    环境记录更新模型
    """
    plot_id: Optional[int] = None
    record_date: Optional[date] = None
    year: Optional[int] = None
    month: Optional[int] = None

    # 水资源
    water_usage: Optional[float] = Field(None, ge=0)
    water_source: Optional[str] = None
    water_cost: Optional[float] = Field(None, ge=0)

    # 能源
    electricity_usage: Optional[float] = Field(None, ge=0)
    electricity_cost: Optional[float] = Field(None, ge=0)
    fuel_usage: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[str] = None
    fuel_cost: Optional[float] = Field(None, ge=0)

    # 农资
    fertilizer_usage: Optional[float] = Field(None, ge=0)
    fertilizer_type: Optional[str] = None
    fertilizer_cost: Optional[float] = Field(None, ge=0)
    pesticide_usage: Optional[float] = Field(None, ge=0)
    pesticide_type: Optional[str] = None
    pesticide_cost: Optional[float] = Field(None, ge=0)
    seed_usage: Optional[float] = Field(None, ge=0)
    seed_type: Optional[str] = None
    seed_cost: Optional[float] = Field(None, ge=0)

    notes: Optional[str] = None


class EnvironmentRecordResponse(EnvironmentRecordBase):
    """
    环境记录响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    plot: Optional[PlotResponse] = None

    class Config:
        from_attributes = True


# ============= 报表相关模型 =============
class ProductionReportRequest(BaseModel):
    """
    生产报表请求模型
    """
    crop_id: Optional[int] = Field(None, description="作物ID，不指定则查询所有")
    plot_id: Optional[int] = Field(None, description="地块ID，不指定则查询所有")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    year: Optional[int] = Field(None, description="年份")
    season: Optional[str] = Field(None, description="季节")


class FinancialReportRequest(BaseModel):
    """
    财务报表请求模型
    """
    record_type: Optional[str] = Field(None, description="类型：income/expense，不指定则查询所有")
    category: Optional[str] = Field(None, description="分类，不指定则查询所有")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    year: Optional[int] = Field(None, description="年份")
    quarter: Optional[int] = Field(None, description="季度")
    month: Optional[int] = Field(None, description="月份")


class EnvironmentReportRequest(BaseModel):
    """
    环境报表请求模型
    """
    plot_id: Optional[int] = Field(None, description="地块ID，不指定则查询所有")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    year: Optional[int] = Field(None, description="年份")
    month: Optional[int] = Field(None, description="月份")


# ============= 通用响应模型 =============
class APIResponse(BaseModel):
    """
    通用API响应模型
    """
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """
    分页响应模型
    """
    success: bool = True
    message: str = "获取成功"
    data: List
    total: int
    page: int
    page_size: int
    total_pages: int
