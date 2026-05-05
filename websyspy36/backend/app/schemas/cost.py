"""
成本核算与利润分析模块的Pydantic数据模型
用于API请求和响应的数据验证
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# ============ 原材料相关模型 ============

class MaterialBase(BaseModel):
    """
    原材料基础模型
    """
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    material_type: Optional[str] = None
    unit: Optional[str] = "吨"
    current_price: Optional[float] = 0.0
    supplier: Optional[str] = None
    stock_quantity: Optional[float] = 0.0


class MaterialCreate(MaterialBase):
    """
    创建原材料模型
    """
    material_code: str
    material_name: str


class MaterialUpdate(MaterialBase):
    """
    更新原材料模型
    """
    pass


class MaterialResponse(MaterialBase):
    """
    原材料响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 原材料成本相关模型 ============

class MaterialCostBase(BaseModel):
    """
    原材料成本基础模型
    """
    record_date: Optional[date] = None
    material_id: Optional[int] = None
    consumption_quantity: Optional[float] = 0.0
    unit_price: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0
    production_batch: Optional[str] = None
    remarks: Optional[str] = None


class MaterialCostCreate(MaterialCostBase):
    """
    创建原材料成本模型
    """
    record_date: date
    material_id: int


class MaterialCostUpdate(MaterialCostBase):
    """
    更新原材料成本模型
    """
    pass


class MaterialCostResponse(MaterialCostBase):
    """
    原材料成本响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    material_name: Optional[str] = None
    material_code: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 员工相关模型 ============

class EmployeeBase(BaseModel):
    """
    员工基础模型
    """
    employee_code: Optional[str] = None
    employee_name: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    base_salary: Optional[float] = 0.0
    hourly_rate: Optional[float] = 0.0
    status: Optional[str] = "在职"


class EmployeeCreate(EmployeeBase):
    """
    创建员工模型
    """
    employee_code: str
    employee_name: str


class EmployeeUpdate(EmployeeBase):
    """
    更新员工模型
    """
    pass


class EmployeeResponse(EmployeeBase):
    """
    员工响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 人工成本相关模型 ============

class LaborCostBase(BaseModel):
    """
    人工成本基础模型
    """
    record_date: Optional[date] = None
    employee_id: Optional[int] = None
    working_hours: Optional[float] = 0.0
    overtime_hours: Optional[float] = 0.0
    hourly_rate: Optional[float] = 0.0
    overtime_rate: Optional[float] = 1.5
    total_labor_cost: Optional[float] = 0.0
    work_content: Optional[str] = None


class LaborCostCreate(LaborCostBase):
    """
    创建人工成本模型
    """
    record_date: date
    employee_id: int


class LaborCostUpdate(LaborCostBase):
    """
    更新人工成本模型
    """
    pass


class LaborCostResponse(LaborCostBase):
    """
    人工成本响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    employee_name: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 销售记录相关模型 ============

class SalesRecordBase(BaseModel):
    """
    销售记录基础模型
    """
    sale_date: Optional[date] = None
    sale_code: Optional[str] = None
    customer_name: Optional[str] = None
    concrete_type: Optional[str] = None
    quantity: Optional[float] = 0.0
    unit_price: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0
    delivery_location: Optional[str] = None
    status: Optional[str] = "已确认"
    remarks: Optional[str] = None


class SalesRecordCreate(SalesRecordBase):
    """
    创建销售记录模型
    """
    sale_date: date
    concrete_type: str
    quantity: float
    unit_price: float


class SalesRecordUpdate(SalesRecordBase):
    """
    更新销售记录模型
    """
    pass


class SalesRecordResponse(SalesRecordBase):
    """
    销售记录响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 利润分析相关模型 ============

class ProfitAnalysisBase(BaseModel):
    """
    利润分析基础模型
    """
    analysis_date: Optional[date] = None
    sales_record_id: Optional[int] = None
    concrete_type: Optional[str] = None
    
    # 成本分解
    material_cost_per_cubic: Optional[float] = 0.0
    labor_cost_per_cubic: Optional[float] = 0.0
    energy_cost_per_cubic: Optional[float] = 0.0
    other_cost_per_cubic: Optional[float] = 0.0
    total_cost_per_cubic: Optional[float] = 0.0
    
    # 收入和利润
    sales_price_per_cubic: Optional[float] = 0.0
    gross_profit_per_cubic: Optional[float] = 0.0
    gross_profit_margin: Optional[float] = 0.0
    
    # 汇总数据
    total_quantity: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0
    total_sales: Optional[float] = 0.0
    total_gross_profit: Optional[float] = 0.0


class ProfitAnalysisCreate(ProfitAnalysisBase):
    """
    创建利润分析模型
    """
    analysis_date: date
    sales_record_id: int


class ProfitAnalysisResponse(ProfitAnalysisBase):
    """
    利润分析响应模型
    """
    id: int
    created_at: datetime
    updated_at: datetime
    customer_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============ 成本统计相关模型 ============

class DailyMaterialCostStats(BaseModel):
    """
    日原材料成本统计
    """
    record_date: date
    material_type: str
    total_quantity: float
    total_cost: float
    unit: str


class MonthlyMaterialCostStats(BaseModel):
    """
    月原材料成本统计
    """
    year: int
    month: int
    material_type: str
    total_quantity: float
    total_cost: float


class LaborCostStats(BaseModel):
    """
    人工成本统计
    """
    record_date: date
    department: str
    total_working_hours: float
    total_overtime_hours: float
    total_labor_cost: float


class UnitCostAnalysis(BaseModel):
    """
    单方成本分析
    """
    concrete_type: str
    average_material_cost: float
    average_labor_cost: float
    average_energy_cost: float
    average_total_cost: float
    average_sales_price: float
    average_gross_profit: float
    average_margin: float
    total_quantity: float
