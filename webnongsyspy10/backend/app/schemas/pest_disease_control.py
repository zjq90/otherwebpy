"""
病虫害防治管理的数据验证模式
定义Pydantic模型，用于API请求和响应的数据验证
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class PestDiseaseTypeEnum(str, Enum):
    """
    病虫害类型枚举
    """
    PEST = "虫害"
    DISEASE = "病害"
    WEED = "草害"
    NEMATODE = "线虫病"
    OTHER = "其他"


class ControlMethodEnum(str, Enum):
    """
    防治措施类型枚举
    """
    BIOLOGICAL = "生物防治"
    PHYSICAL = "物理防治"
    CHEMICAL = "化学防治"
    AGRICULTURAL = "农业防治"
    COMBINED = "综合防治"


class SeverityLevelEnum(str, Enum):
    """
    严重程度枚举
    """
    LIGHT = "轻度"
    MODERATE = "中度"
    SEVERE = "重度"
    VERY_SEVERE = "极重度"


class TreatmentStatusEnum(str, Enum):
    """
    防治状态枚举
    """
    DETECTED = "已发现"
    TREATING = "防治中"
    CONTROLLED = "已控制"
    ERADICATED = "已根除"
    REOCCURRING = "复发"


class PestDiseaseControlBase(BaseModel):
    """
    病虫害防治基础模型
    """
    discovery_date: date = Field(..., description="发现日期")
    pest_disease_type: PestDiseaseTypeEnum = Field(..., description="病虫害类型")
    pest_disease_name: str = Field(..., max_length=200, description="病虫害名称")
    scientific_name: Optional[str] = Field(None, max_length=200, description="病虫害学名")
    crop_type: Optional[str] = Field(None, max_length=100, description="受害作物种类")
    crop_variety: Optional[str] = Field(None, max_length=100, description="受害作物品种")
    growth_stage: Optional[str] = Field(None, max_length=100, description="作物生育期")
    plot_location: Optional[str] = Field(None, max_length=200, description="发生地块")
    affected_area: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="影响面积（亩）")
    severity: Optional[SeverityLevelEnum] = Field(None, description="严重程度")
    incidence_rate: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="发生率（%）")
    symptoms_description: Optional[str] = Field(None, description="危害症状描述")
    photo_urls: Optional[str] = Field(None, description="现场照片URL")
    
    # 防治措施
    control_method: Optional[ControlMethodEnum] = Field(None, description="防治措施类型")
    treatment_date: Optional[date] = Field(None, description="防治日期")
    operator: Optional[str] = Field(None, max_length=100, description="操作人员")
    
    # 化学防治专用字段
    pesticide_name: Optional[str] = Field(None, max_length=200, description="药剂名称")
    pesticide_type: Optional[str] = Field(None, max_length=50, description="药剂类型")
    registration_number: Optional[str] = Field(None, max_length=100, description="农药登记证号")
    manufacturer: Optional[str] = Field(None, max_length=200, description="生产厂家")
    dosage_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="使用剂量（每亩）")
    dosage_unit: Optional[str] = Field(None, max_length=20, description="剂量单位")
    dilution_ratio: Optional[int] = Field(None, ge=1, description="稀释倍数")
    application_method: Optional[str] = Field(None, max_length=200, description="施药方法")
    equipment_used: Optional[str] = Field(None, max_length=200, description="施药器械")
    safety_interval_days: Optional[int] = Field(None, ge=0, description="安全间隔期（天）")
    allowed_use_date: Optional[date] = Field(None, description="允许使用日期")
    
    # 生物防治专用字段
    natural_enemy_type: Optional[str] = Field(None, max_length=200, description="天敌种类")
    release_quantity: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=2, description="释放数量")
    release_method: Optional[str] = Field(None, max_length=200, description="释放方式")
    
    # 物理防治专用字段
    physical_measure_type: Optional[str] = Field(None, max_length=200, description="物理措施类型")
    quantity_density: Optional[str] = Field(None, max_length=100, description="数量/密度")
    
    # 效果评估
    treatment_status: TreatmentStatusEnum = Field(default=TreatmentStatusEnum.DETECTED, description="防治状态")
    assessment_date: Optional[date] = Field(None, description="防治效果评估日期")
    control_effect: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="防治效果（%）")
    effect_description: Optional[str] = Field(None, description="效果描述")
    needs_retreatment: bool = Field(default=False, description="是否需要再次防治")
    suggested_retreatment_date: Optional[date] = Field(None, description="建议再次防治日期")
    
    # 其他信息
    weather_condition: Optional[str] = Field(None, max_length=100, description="作业时天气情况")
    remarks: Optional[str] = Field(None, description="备注说明")


class PestDiseaseControlCreate(PestDiseaseControlBase):
    """
    病虫害防治创建模型
    """
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    record_code: str = Field(..., max_length=50, description="记录编号")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")


class PestDiseaseControlUpdate(BaseModel):
    """
    病虫害防治更新模型
    """
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    discovery_date: Optional[date] = Field(None, description="发现日期")
    pest_disease_type: Optional[PestDiseaseTypeEnum] = Field(None, description="病虫害类型")
    pest_disease_name: Optional[str] = Field(None, max_length=200, description="病虫害名称")
    scientific_name: Optional[str] = Field(None, max_length=200, description="病虫害学名")
    crop_type: Optional[str] = Field(None, max_length=100, description="受害作物种类")
    crop_variety: Optional[str] = Field(None, max_length=100, description="受害作物品种")
    growth_stage: Optional[str] = Field(None, max_length=100, description="作物生育期")
    plot_location: Optional[str] = Field(None, max_length=200, description="发生地块")
    affected_area: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="影响面积（亩）")
    severity: Optional[SeverityLevelEnum] = Field(None, description="严重程度")
    incidence_rate: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="发生率（%）")
    symptoms_description: Optional[str] = Field(None, description="危害症状描述")
    photo_urls: Optional[str] = Field(None, description="现场照片URL")
    control_method: Optional[ControlMethodEnum] = Field(None, description="防治措施类型")
    treatment_date: Optional[date] = Field(None, description="防治日期")
    operator: Optional[str] = Field(None, max_length=100, description="操作人员")
    pesticide_name: Optional[str] = Field(None, max_length=200, description="药剂名称")
    pesticide_type: Optional[str] = Field(None, max_length=50, description="药剂类型")
    registration_number: Optional[str] = Field(None, max_length=100, description="农药登记证号")
    manufacturer: Optional[str] = Field(None, max_length=200, description="生产厂家")
    dosage_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="使用剂量（每亩）")
    dosage_unit: Optional[str] = Field(None, max_length=20, description="剂量单位")
    dilution_ratio: Optional[int] = Field(None, ge=1, description="稀释倍数")
    application_method: Optional[str] = Field(None, max_length=200, description="施药方法")
    equipment_used: Optional[str] = Field(None, max_length=200, description="施药器械")
    safety_interval_days: Optional[int] = Field(None, ge=0, description="安全间隔期（天）")
    allowed_use_date: Optional[date] = Field(None, description="允许使用日期")
    natural_enemy_type: Optional[str] = Field(None, max_length=200, description="天敌种类")
    release_quantity: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=2, description="释放数量")
    release_method: Optional[str] = Field(None, max_length=200, description="释放方式")
    physical_measure_type: Optional[str] = Field(None, max_length=200, description="物理措施类型")
    quantity_density: Optional[str] = Field(None, max_length=100, description="数量/密度")
    treatment_status: Optional[TreatmentStatusEnum] = Field(None, description="防治状态")
    assessment_date: Optional[date] = Field(None, description="防治效果评估日期")
    control_effect: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="防治效果（%）")
    effect_description: Optional[str] = Field(None, description="效果描述")
    needs_retreatment: Optional[bool] = Field(None, description="是否需要再次防治")
    suggested_retreatment_date: Optional[date] = Field(None, description="建议再次防治日期")
    weather_condition: Optional[str] = Field(None, max_length=100, description="作业时天气情况")
    remarks: Optional[str] = Field(None, description="备注说明")


class PestDiseaseControlResponse(PestDiseaseControlBase):
    """
    病虫害防治响应模型
    """
    id: int = Field(..., description="记录ID")
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    record_code: str = Field(..., max_length=50, description="记录编号")
    
    # 高毒农药预警相关
    is_high_toxic: bool = Field(default=False, description="是否为高毒农药")
    has_warning: bool = Field(default=False, description="是否触发预警")
    warning_message: Optional[str] = Field(None, description="预警信息")
    
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")

    class Config:
        from_attributes = True


class PestDiseaseControlListResponse(BaseModel):
    """
    病虫害防治列表响应模型
    """
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: list[PestDiseaseControlResponse] = Field(..., description="记录列表")

    class Config:
        from_attributes = True


class WarningResponse(BaseModel):
    """
    预警响应模型
    """
    has_warning: bool = Field(..., description="是否有预警")
    warning_count: int = Field(..., description="预警数量")
    warnings: list[dict] = Field(default=[], description="预警详情列表")
