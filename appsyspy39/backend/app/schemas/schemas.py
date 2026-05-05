"""
Pydantic模型（Schemas）- 用于API请求和响应的数据验证
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== 用户相关模型 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    role: Optional[str] = Field("operator", description="角色：operator-操作员, admin-管理员")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int = Field(..., description="总数")
    users: List[UserResponse] = Field(..., description="用户列表")


# ==================== Token相关模型 ====================

class Token(BaseModel):
    """Token响应模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    role: Optional[str] = Field(None, description="角色")


# ==================== 配方相关模型 ====================

class FormulaBase(BaseModel):
    """配方基础模型"""
    formula_name: str = Field(..., max_length=100, description="配方名称")
    formula_code: str = Field(..., max_length=50, description="配方编号")
    concrete_grade: str = Field(..., max_length=20, description="适用混凝土标号")
    water_cement_ratio: float = Field(..., gt=0, description="水灰比")
    slump: Optional[float] = Field(None, ge=0, description="坍落度（mm）")
    cement: float = Field(..., ge=0, description="水泥用量(kg/m³)")
    water: float = Field(..., ge=0, description="用水量(kg/m³)")
    sand: float = Field(..., ge=0, description="砂子用量(kg/m³)")
    stone: float = Field(..., ge=0, description="石子用量(kg/m³)")
    admixture: Optional[float] = Field(None, ge=0, description="外加剂用量(kg/m³)")
    admixture_type: Optional[str] = Field(None, max_length=50, description="外加剂类型")
    fly_ash: Optional[float] = Field(0, ge=0, description="粉煤灰用量(kg/m³)")
    mineral_powder: Optional[float] = Field(0, ge=0, description="矿粉用量(kg/m³)")
    is_active: Optional[bool] = Field(True, description="是否启用")
    is_standard: Optional[bool] = Field(True, description="是否标准配方")
    remarks: Optional[str] = Field(None, description="备注说明")


class FormulaCreate(FormulaBase):
    """配方创建模型"""
    pass


class FormulaUpdate(BaseModel):
    """配方更新模型"""
    formula_name: Optional[str] = Field(None, max_length=100)
    water_cement_ratio: Optional[float] = Field(None, gt=0)
    cement: Optional[float] = Field(None, ge=0)
    water: Optional[float] = Field(None, ge=0)
    sand: Optional[float] = Field(None, ge=0)
    stone: Optional[float] = Field(None, ge=0)
    admixture: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    remarks: Optional[str] = None


class FormulaResponse(FormulaBase):
    """配方响应模型"""
    id: int = Field(..., description="配方ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class FormulaListResponse(BaseModel):
    """配方列表响应"""
    total: int = Field(..., description="总数")
    formulas: List[FormulaResponse] = Field(..., description="配方列表")


class FormulaAdjustmentCreate(BaseModel):
    """配方调整创建模型"""
    task_id: int = Field(..., description="任务ID")
    base_formula_id: int = Field(..., description="基础配方ID")
    adjustment_reason: str = Field(..., description="调整原因")
    
    # 调整后的参数
    new_water_cement_ratio: Optional[float] = Field(None, description="新水灰比")
    new_cement: Optional[float] = Field(None, ge=0, description="新水泥用量")
    new_water: Optional[float] = Field(None, ge=0, description="新用水量")
    new_sand: Optional[float] = Field(None, ge=0, description="新砂子用量")
    new_stone: Optional[float] = Field(None, ge=0, description="新石子用量")
    new_admixture: Optional[float] = Field(None, ge=0, description="新外加剂用量")
    new_admixture_dosage: Optional[float] = Field(None, description="新外加剂掺量百分比")
    
    remarks: Optional[str] = Field(None, description="备注")


class FormulaAdjustmentResponse(BaseModel):
    """配方调整响应模型"""
    id: int
    task_id: int
    base_formula_id: int
    adjustment_reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 任务相关模型 ====================

class TaskBase(BaseModel):
    """任务基础模型"""
    task_no: str = Field(..., max_length=50, description="任务编号")
    concrete_grade: str = Field(..., max_length=20, description="混凝土标号")
    quantity: float = Field(..., gt=0, description="生产数量（立方米）")
    delivery_time: datetime = Field(..., description="交货时间")
    project_name: str = Field(..., max_length=100, description="项目名称")
    project_address: Optional[str] = Field(None, max_length=200, description="项目地址")
    customer_name: Optional[str] = Field(None, max_length=50, description="客户名称")
    formula_id: Optional[int] = Field(None, description="使用的配方ID")
    remarks: Optional[str] = Field(None, description="备注")


class TaskCreate(TaskBase):
    """任务创建模型"""
    pass


class TaskUpdate(BaseModel):
    """任务更新模型"""
    concrete_grade: Optional[str] = None
    quantity: Optional[float] = Field(None, gt=0)
    delivery_time: Optional[datetime] = None
    project_name: Optional[str] = None
    formula_id: Optional[int] = None
    remarks: Optional[str] = None


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int = Field(..., description="任务ID")
    status: str = Field(..., description="状态")
    operator_id: Optional[int] = Field(None, description="接单人ID")
    operator_name: Optional[str] = Field(None, description="接单人姓名")
    accepted_at: Optional[datetime] = Field(None, description="接单时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    formula_info: Optional[FormulaResponse] = Field(None, description="配方信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int = Field(..., description="总数")
    tasks: List[TaskResponse] = Field(..., description="任务列表")


# ==================== 投料记录相关模型 ====================

class FeedingRecordCreate(BaseModel):
    """投料记录创建模型"""
    task_id: int = Field(..., description="任务ID")
    batch_no: int = Field(..., ge=1, description="盘号")
    batch_quantity: float = Field(..., gt=0, description="本盘方量")
    feeding_method: str = Field(default="manual", description="投料方式：scan-扫码录入, manual-手动录入")
    
    # 原材料实际用量
    cement_actual: Optional[float] = Field(None, ge=0, description="水泥实际用量")
    water_actual: Optional[float] = Field(None, ge=0, description="水实际用量")
    sand_actual: Optional[float] = Field(None, ge=0, description="砂子实际用量")
    stone_actual: Optional[float] = Field(None, ge=0, description="石子实际用量")
    admixture_actual: Optional[float] = Field(None, ge=0, description="外加剂实际用量")
    fly_ash_actual: Optional[float] = Field(0, ge=0, description="粉煤灰实际用量")
    mineral_powder_actual: Optional[float] = Field(0, ge=0, description="矿粉实际用量")
    
    # 原材料扫码信息
    cement_barcode: Optional[str] = Field(None, max_length=100)
    cement_lot: Optional[str] = Field(None, max_length=50)
    sand_barcode: Optional[str] = Field(None, max_length=100)
    sand_lot: Optional[str] = Field(None, max_length=50)
    stone_barcode: Optional[str] = Field(None, max_length=100)
    stone_lot: Optional[str] = Field(None, max_length=50)
    admixture_barcode: Optional[str] = Field(None, max_length=100)
    admixture_lot: Optional[str] = Field(None, max_length=50)
    
    remarks: Optional[str] = Field(None, description="备注")


class FeedingRecordResponse(BaseModel):
    """投料记录响应模型"""
    id: int
    task_id: int
    batch_no: int
    batch_quantity: float
    feeding_method: str
    
    # 实际用量
    cement_actual: Optional[float]
    water_actual: Optional[float]
    sand_actual: Optional[float]
    stone_actual: Optional[float]
    admixture_actual: Optional[float]
    
    # 理论用量
    cement_theory: Optional[float]
    water_theory: Optional[float]
    sand_theory: Optional[float]
    stone_theory: Optional[float]
    admixture_theory: Optional[float]
    
    # 偏差
    cement_deviation: Optional[float]
    water_deviation: Optional[float]
    sand_deviation: Optional[float]
    stone_deviation: Optional[float]
    admixture_deviation: Optional[float]
    
    # 预警
    has_warning: bool
    warning_level: Optional[str]
    warning_message: Optional[str]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedingRecordListResponse(BaseModel):
    """投料记录列表响应"""
    total: int
    records: List[FeedingRecordResponse]


# ==================== 搅拌记录相关模型 ====================

class MixingRecordCreate(BaseModel):
    """搅拌记录创建模型"""
    task_id: int = Field(..., description="任务ID")
    feeding_record_id: Optional[int] = Field(None, description="关联投料记录ID")
    batch_no: int = Field(..., ge=1, description="盘号")
    
    # 搅拌参数
    mixing_time_seconds: int = Field(..., ge=0, description="搅拌时长（秒）")
    rotation_speed: Optional[int] = Field(None, ge=0, description="搅拌转速（RPM）")
    current_temperature: Optional[float] = Field(None, description="当前温度（℃）")
    
    # 异常记录
    is_abnormal: Optional[bool] = Field(False, description="是否异常")
    abnormal_type: Optional[str] = Field(None, description="异常类型")
    abnormal_description: Optional[str] = Field(None, description="异常情况说明")
    handling_measures: Optional[str] = Field(None, description="处理措施")
    
    # 质量检验
    slump_actual: Optional[float] = Field(None, description="实测坍落度（mm）")
    temperature_actual: Optional[float] = Field(None, description="实测温度（℃）")
    quality_status: Optional[str] = Field(None, description="质量状态")
    
    remarks: Optional[str] = Field(None, description="备注")


class MixingRecordResponse(BaseModel):
    """搅拌记录响应模型"""
    id: int
    task_id: int
    batch_no: int
    mixing_time_seconds: int
    rotation_speed: Optional[int]
    current_temperature: Optional[float]
    status: str
    
    is_abnormal: bool
    abnormal_type: Optional[str]
    abnormal_description: Optional[str]
    
    slump_actual: Optional[float]
    quality_status: Optional[str]
    
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MixingRecordListResponse(BaseModel):
    """搅拌记录列表响应"""
    total: int
    records: List[MixingRecordResponse]


# ==================== 通用响应模型 ====================

class SuccessResponse(BaseModel):
    """通用成功响应"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error_code: str = "UNKNOWN_ERROR"
    message: str = "操作失败"
    details: Optional[dict] = None
