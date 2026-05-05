"""
Pydantic数据模型定义
用于API请求和响应的数据验证和序列化
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    role: str = Field(default="inspector", description="角色: inspector-检验员, admin-管理员")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


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


class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


class MaterialBase(BaseModel):
    """原材料基础模型"""
    material_code: str = Field(..., max_length=50, description="原材料编码")
    material_name: str = Field(..., max_length=100, description="原材料名称")
    material_type: str = Field(..., max_length=50, description="类型: cement-水泥, aggregate-骨料, admixture-外加剂")
    supplier: Optional[str] = Field(None, max_length=100, description="供应商")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    unit: str = Field(default="吨", max_length=20, description="单位")


class MaterialCreate(MaterialBase):
    """原材料创建模型"""
    pass


class MaterialUpdate(BaseModel):
    """原材料更新模型"""
    material_name: Optional[str] = None
    material_type: Optional[str] = None
    supplier: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class MaterialResponse(MaterialBase):
    """原材料响应模型"""
    id: int = Field(..., description="原材料ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class MaterialInspectionBase(BaseModel):
    """原材料检验基础模型"""
    material_id: int = Field(..., description="原材料ID")
    batch_no: str = Field(..., max_length=100, description="批次号")
    arrival_date: datetime = Field(..., description="进场日期")
    
    # 检验指标
    cement_strength_3d: Optional[float] = Field(None, description="水泥3天强度")
    cement_strength_28d: Optional[float] = Field(None, description="水泥28天强度")
    cement_fineness: Optional[float] = Field(None, description="水泥细度")
    aggregate_gradation: Optional[str] = Field(None, description="骨料级配数据(JSON)")
    admixture_performance: Optional[str] = Field(None, description="外加剂性能数据(JSON)")
    water_content: Optional[float] = Field(None, description="含水量")
    impurity_content: Optional[float] = Field(None, description="杂质含量")
    
    inspection_report: Optional[str] = Field(None, max_length=255, description="检验报告附件路径")
    remarks: Optional[str] = Field(None, description="备注")


class MaterialInspectionCreate(MaterialInspectionBase):
    """原材料检验创建模型"""
    pass


class MaterialInspectionResponse(MaterialInspectionBase):
    """原材料检验响应模型"""
    id: int = Field(..., description="检验记录ID")
    inspection_no: str = Field(..., max_length=50, description="检验单号")
    inspector_id: int = Field(..., description="检验员ID")
    inspection_date: datetime = Field(..., description="检验日期")
    is_qualified: bool = Field(..., description="是否合格")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    
    material: Optional[MaterialResponse] = None
    
    class Config:
        from_attributes = True


class ProductionFormulaBase(BaseModel):
    """生产配方基础模型"""
    formula_code: str = Field(..., max_length=50, description="配方编码")
    formula_name: str = Field(..., max_length=100, description="配方名称")
    concrete_grade: str = Field(..., max_length=20, description="混凝土强度等级")
    description: Optional[str] = Field(None, description="描述")
    
    # 配方比例
    cement_amount: float = Field(..., description="水泥用量(kg/m³)")
    sand_amount: float = Field(..., description="砂用量(kg/m³)")
    stone_amount: float = Field(..., description="石用量(kg/m³)")
    water_amount: float = Field(..., description="水用量(kg/m³)")
    admixture_amount: Optional[float] = Field(None, description="外加剂用量(kg/m³)")
    fly_ash_amount: Optional[float] = Field(None, description="粉煤灰用量(kg/m³)")
    
    # 允许偏差
    cement_tolerance: float = Field(default=2.0, description="水泥允许偏差±%")
    aggregate_tolerance: float = Field(default=3.0, description="骨料允许偏差±%")
    water_tolerance: float = Field(default=1.0, description="水允许偏差±%")


class ProductionFormulaCreate(ProductionFormulaBase):
    """生产配方创建模型"""
    pass


class ProductionFormulaResponse(ProductionFormulaBase):
    """生产配方响应模型"""
    id: int = Field(..., description="配方ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class ProductionRecordBase(BaseModel):
    """生产记录基础模型"""
    formula_id: int = Field(..., description="配方ID")
    truck_no: str = Field(..., max_length=20, description="罐车编号")
    mix_volume: float = Field(..., description="搅拌方量")
    mix_duration: int = Field(..., description="搅拌时间(秒)")
    target_mix_duration: int = Field(..., description="目标搅拌时间(秒)")
    feeding_data: Optional[str] = Field(None, description="投料数据(JSON)")
    status: str = Field(default="正常", description="状态: normal-正常, abnormal-异常")


class ProductionRecordCreate(ProductionRecordBase):
    """生产记录创建模型"""
    pass


class ProductionRecordResponse(ProductionRecordBase):
    """生产记录响应模型"""
    id: int = Field(..., description="生产记录ID")
    production_no: str = Field(..., max_length=50, description="生产单号")
    qr_code: str = Field(..., max_length=100, description="二维码标识")
    operator_id: Optional[int] = Field(None, description="操作员ID")
    production_date: datetime = Field(..., description="生产日期")
    created_at: datetime = Field(..., description="创建时间")
    
    formula: Optional[ProductionFormulaResponse] = None
    
    class Config:
        from_attributes = True


class QualityAlertBase(BaseModel):
    """质量预警基础模型"""
    production_id: int = Field(..., description="生产记录ID")
    alert_type: str = Field(..., max_length=50, description="预警类型: mix_ratio_deviation-配比偏差, mix_time_short-搅拌时间不足, material_unqualified-原材料不合格")
    alert_level: str = Field(default="一般", description="预警级别: 一般-normal, 严重-serious, 紧急-urgent")
    description: str = Field(..., description="预警描述")
    deviation_data: Optional[str] = Field(None, description="偏差数据(JSON)")


class QualityAlertCreate(QualityAlertBase):
    """质量预警创建模型"""
    pass


class QualityAlertUpdate(BaseModel):
    """质量预警更新模型"""
    status: Optional[str] = None
    handler_id: Optional[int] = None
    handle_time: Optional[datetime] = None
    handle_result: Optional[str] = None


class QualityAlertResponse(QualityAlertBase):
    """质量预警响应模型"""
    id: int = Field(..., description="预警ID")
    alert_no: str = Field(..., max_length=50, description="预警编号")
    status: str = Field(..., description="状态: pending-待处理, processing-处理中, resolved-已处理")
    handler_id: Optional[int] = Field(None, description="处理人ID")
    handle_time: Optional[datetime] = Field(None, description="处理时间")
    handle_result: Optional[str] = Field(None, description="处理结果")
    created_at: datetime = Field(..., description="创建时间")
    
    production: Optional[ProductionRecordResponse] = None
    
    class Config:
        from_attributes = True


class InspectionReportBase(BaseModel):
    """检验报告基础模型"""
    production_id: int = Field(..., description="生产记录ID")
    report_type: str = Field(..., max_length=50, description="报告类型: factory-出厂检验, site-现场检验")
    inspection_date: datetime = Field(..., description="检验日期")
    
    # 检验指标
    slump: Optional[float] = Field(None, description="坍落度")
    air_content: Optional[float] = Field(None, description="含气量")
    temperature: Optional[float] = Field(None, description="温度")
    strength_7d: Optional[float] = Field(None, description="7天强度")
    strength_28d: Optional[float] = Field(None, description="28天强度")
    
    report_file: Optional[str] = Field(None, max_length=255, description="报告文件路径")
    is_qualified: bool = Field(default=True, description="是否合格")
    remarks: Optional[str] = Field(None, description="备注")


class InspectionReportCreate(InspectionReportBase):
    """检验报告创建模型"""
    pass


class InspectionReportResponse(InspectionReportBase):
    """检验报告响应模型"""
    id: int = Field(..., description="报告ID")
    report_no: str = Field(..., max_length=50, description="报告编号")
    inspector_id: int = Field(..., description="检验员ID")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class FeedingRecordBase(BaseModel):
    """投料记录基础模型"""
    production_id: int = Field(..., description="生产记录ID")
    material_type: str = Field(..., max_length=50, description="材料类型")
    target_amount: float = Field(..., description="目标用量")
    actual_amount: float = Field(..., description="实际用量")
    deviation: Optional[float] = Field(None, description="偏差量")
    deviation_percent: Optional[float] = Field(None, description="偏差百分比")


class FeedingRecordCreate(FeedingRecordBase):
    """投料记录创建模型"""
    pass


class FeedingRecordResponse(FeedingRecordBase):
    """投料记录响应模型"""
    id: int = Field(..., description="记录ID")
    feeding_time: datetime = Field(..., description="投料时间")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class QualityTraceResponse(BaseModel):
    """质量追溯响应模型"""
    production: ProductionRecordResponse = Field(..., description="生产记录")
    formula: ProductionFormulaResponse = Field(..., description="生产配方")
    feeding_records: List[FeedingRecordResponse] = Field(default_factory=list, description="投料记录")
    inspection_reports: List[InspectionReportResponse] = Field(default_factory=list, description="检验报告")
    alerts: List[QualityAlertResponse] = Field(default_factory=list, description="关联预警")


class ApiResponse(BaseModel):
    """通用API响应模型"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: Optional[dict] = Field(None, description="数据")


class PaginatedResponse(ApiResponse):
    """分页响应模型"""
    total: int = Field(0, description="总记录数")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页大小")


class TestDataGenerateRequest(BaseModel):
    """测试数据生成请求模型"""
    generate_users: bool = Field(default=True, description="是否生成用户")
    generate_materials: bool = Field(default=True, description="是否生成原材料")
    generate_formulas: bool = Field(default=True, description="是否生成配方")
    generate_inspections: bool = Field(default=True, description="是否生成检验记录")
    generate_productions: bool = Field(default=True, description="是否生成生产记录")
    generate_alerts: bool = Field(default=True, description="是否生成预警")
    generate_reports: bool = Field(default=True, description="是否生成报告")
    count_inspections: int = Field(default=10, description="检验记录数量")
    count_productions: int = Field(default=15, description="生产记录数量")


class TestAccount(BaseModel):
    """测试账号信息"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    role: str = Field(..., description="角色")


class TestDataGenerateResponse(BaseModel):
    """测试数据生成响应模型"""
    users_created: int = Field(0, description="创建的用户数量")
    materials_created: int = Field(0, description="创建的原材料数量")
    formulas_created: int = Field(0, description="创建的配方数量")
    inspections_created: int = Field(0, description="创建的检验记录数量")
    productions_created: int = Field(0, description="创建的生产记录数量")
    alerts_created: int = Field(0, description="创建的预警数量")
    reports_created: int = Field(0, description="创建的报告数量")
    test_accounts: Optional[dict] = Field(None, description="测试账号信息")


class TestDataStatusResponse(BaseModel):
    """测试数据状态响应模型"""
    has_test_data: bool = Field(..., description="是否有测试数据")
    user_count: int = Field(0, description="用户数量")
    material_count: int = Field(0, description="原材料数量")
    formula_count: int = Field(0, description="配方数量")
    inspection_count: int = Field(0, description="检验记录数量")
    production_count: int = Field(0, description="生产记录数量")
    alert_count: int = Field(0, description="预警数量")
    report_count: int = Field(0, description="报告数量")
