"""
精准施肥与灌溉的数据验证模式
定义Pydantic模型，用于API请求和响应的数据验证
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class FertilizerTypeEnum(str, Enum):
    """
    肥料类型枚举
    """
    NITROGEN = "氮肥"
    PHOSPHATE = "磷肥"
    POTASSIUM = "钾肥"
    COMPOUND = "复合肥"
    ORGANIC = "有机肥"
    MICROELEMENT = "微肥"
    BIOLOGICAL = "生物肥"
    OTHER = "其他"


class IrrigationTypeEnum(str, Enum):
    """
    灌溉类型枚举
    """
    DRIP = "滴灌"
    SPRINKLER = "喷灌"
    FLOOD = "漫灌"
    SUBSURFACE = "渗灌"
    FERTIGATION = "水肥一体化"
    OTHER = "其他"


class WaterSourceEnum(str, Enum):
    """
    水源类型枚举
    """
    RIVER = "河水"
    LAKE = "湖水"
    GROUNDWATER = "地下水"
    RESERVOIR = "水库"
    RAINWATER = "雨水"
    TAP = "自来水"
    OTHER = "其他"


class FertilizationIrrigationBase(BaseModel):
    """
    精准施肥与灌溉基础模型
    """
    record_type: str = Field(..., max_length=20, description="记录类型：施肥/灌溉/水肥一体化")
    record_date: date = Field(..., description="记录日期")
    crop_type: Optional[str] = Field(None, max_length=100, description="作物种类")
    growth_stage: Optional[str] = Field(None, max_length=100, description="作物生育期")
    plot_location: Optional[str] = Field(None, max_length=200, description="作业地块")
    operation_area: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="作业面积（亩）")
    
    # 土壤检测数据
    soil_test_date: Optional[date] = Field(None, description="土壤检测日期")
    soil_ph: Optional[Decimal] = Field(None, ge=0, le=14, max_digits=5, decimal_places=2, description="土壤pH值")
    organic_matter: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="有机质含量（g/kg）")
    total_nitrogen: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="全氮含量（g/kg）")
    available_phosphorus: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="有效磷含量（mg/kg）")
    available_potassium: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="速效钾含量（mg/kg）")
    alkali_hydrolyzable_nitrogen: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="碱解氮含量（mg/kg）")
    soil_moisture: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="土壤湿度（%）")
    
    # 计划施肥数据
    planned_fertilizer_type: Optional[FertilizerTypeEnum] = Field(None, description="计划肥料类型")
    planned_fertilizer_name: Optional[str] = Field(None, max_length=200, description="计划肥料名称")
    planned_fertilizer_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="计划施肥量（公斤/亩）")
    planned_fertilization_method: Optional[str] = Field(None, max_length=200, description="计划施肥方法")
    
    # 实际施肥数据
    actual_fertilizer_type: Optional[FertilizerTypeEnum] = Field(None, description="实际肥料类型")
    actual_fertilizer_name: Optional[str] = Field(None, max_length=200, description="实际肥料名称")
    actual_fertilizer_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="实际施肥量（公斤/亩）")
    actual_fertilization_method: Optional[str] = Field(None, max_length=200, description="实际施肥方法")
    fertilization_date: Optional[date] = Field(None, description="实际施肥日期")
    
    # 计划灌溉数据
    planned_irrigation_type: Optional[IrrigationTypeEnum] = Field(None, description="计划灌溉类型")
    planned_water_source: Optional[WaterSourceEnum] = Field(None, description="计划水源类型")
    planned_irrigation_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="计划灌溉量（立方米/亩）")
    planned_irrigation_duration: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="计划灌溉时间（小时）")
    
    # 实际灌溉数据
    actual_irrigation_type: Optional[IrrigationTypeEnum] = Field(None, description="实际灌溉类型")
    actual_water_source: Optional[WaterSourceEnum] = Field(None, description="实际水源类型")
    actual_irrigation_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="实际灌溉量（立方米/亩）")
    actual_irrigation_duration: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="实际灌溉时间（小时）")
    irrigation_date: Optional[date] = Field(None, description="实际灌溉日期")
    
    # 水肥一体化
    is_fertigation: int = Field(default=0, ge=0, le=1, description="是否水肥一体化：0-否，1-是")
    fertigation_ratio: Optional[str] = Field(None, max_length=50, description="水肥配比（肥料:水）")
    
    # 其他信息
    operator: Optional[str] = Field(None, max_length=100, description="操作人员")
    equipment_code: Optional[str] = Field(None, max_length=100, description="设备编号")
    weather_condition: Optional[str] = Field(None, max_length=100, description="作业时天气情况")
    remarks: Optional[str] = Field(None, description="备注说明")


class FertilizationIrrigationCreate(FertilizationIrrigationBase):
    """
    精准施肥与灌溉创建模型
    """
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    record_code: str = Field(..., max_length=50, description="记录编号")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")


class FertilizationIrrigationUpdate(BaseModel):
    """
    精准施肥与灌溉更新模型
    """
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    record_type: Optional[str] = Field(None, max_length=20, description="记录类型")
    record_date: Optional[date] = Field(None, description="记录日期")
    crop_type: Optional[str] = Field(None, max_length=100, description="作物种类")
    growth_stage: Optional[str] = Field(None, max_length=100, description="作物生育期")
    plot_location: Optional[str] = Field(None, max_length=200, description="作业地块")
    operation_area: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="作业面积（亩）")
    soil_test_date: Optional[date] = Field(None, description="土壤检测日期")
    soil_ph: Optional[Decimal] = Field(None, ge=0, le=14, max_digits=5, decimal_places=2, description="土壤pH值")
    organic_matter: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="有机质含量")
    total_nitrogen: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="全氮含量")
    available_phosphorus: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="有效磷含量")
    available_potassium: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="速效钾含量")
    alkali_hydrolyzable_nitrogen: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="碱解氮含量")
    soil_moisture: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="土壤湿度")
    planned_fertilizer_type: Optional[FertilizerTypeEnum] = Field(None, description="计划肥料类型")
    planned_fertilizer_name: Optional[str] = Field(None, max_length=200, description="计划肥料名称")
    planned_fertilizer_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="计划施肥量")
    planned_fertilization_method: Optional[str] = Field(None, max_length=200, description="计划施肥方法")
    actual_fertilizer_type: Optional[FertilizerTypeEnum] = Field(None, description="实际肥料类型")
    actual_fertilizer_name: Optional[str] = Field(None, max_length=200, description="实际肥料名称")
    actual_fertilizer_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="实际施肥量")
    actual_fertilization_method: Optional[str] = Field(None, max_length=200, description="实际施肥方法")
    fertilization_date: Optional[date] = Field(None, description="实际施肥日期")
    planned_irrigation_type: Optional[IrrigationTypeEnum] = Field(None, description="计划灌溉类型")
    planned_water_source: Optional[WaterSourceEnum] = Field(None, description="计划水源类型")
    planned_irrigation_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="计划灌溉量")
    planned_irrigation_duration: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="计划灌溉时间")
    actual_irrigation_type: Optional[IrrigationTypeEnum] = Field(None, description="实际灌溉类型")
    actual_water_source: Optional[WaterSourceEnum] = Field(None, description="实际水源类型")
    actual_irrigation_amount_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=3, description="实际灌溉量")
    actual_irrigation_duration: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=2, description="实际灌溉时间")
    irrigation_date: Optional[date] = Field(None, description="实际灌溉日期")
    is_fertigation: Optional[int] = Field(None, ge=0, le=1, description="是否水肥一体化")
    fertigation_ratio: Optional[str] = Field(None, max_length=50, description="水肥配比")
    operator: Optional[str] = Field(None, max_length=100, description="操作人员")
    equipment_code: Optional[str] = Field(None, max_length=100, description="设备编号")
    weather_condition: Optional[str] = Field(None, max_length=100, description="作业时天气情况")
    remarks: Optional[str] = Field(None, description="备注说明")


class FertilizationIrrigationResponse(FertilizationIrrigationBase):
    """
    精准施肥与灌溉响应模型
    """
    id: int = Field(..., description="记录ID")
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    record_code: str = Field(..., max_length=50, description="记录编号")
    
    # 总量数据
    planned_total_fertilizer: Optional[Decimal] = Field(None, max_digits=12, decimal_places=3, description="计划总施肥量（公斤）")
    actual_total_fertilizer: Optional[Decimal] = Field(None, max_digits=12, decimal_places=3, description="实际总施肥量（公斤）")
    planned_total_irrigation: Optional[Decimal] = Field(None, max_digits=12, decimal_places=3, description="计划总灌溉量（立方米）")
    actual_total_irrigation: Optional[Decimal] = Field(None, max_digits=12, decimal_places=3, description="实际总灌溉量（立方米）")
    
    # 对比分析数据
    fertilizer_deviation_percent: Optional[Decimal] = Field(None, max_digits=8, decimal_places=2, description="施肥量偏差（%）")
    irrigation_deviation_percent: Optional[Decimal] = Field(None, max_digits=8, decimal_places=2, description="灌溉量偏差（%）")
    is_according_to_plan: int = Field(default=1, ge=0, le=1, description="是否符合计划：0-否，1-是")
    
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")

    class Config:
        from_attributes = True


class FertilizationIrrigationListResponse(BaseModel):
    """
    精准施肥与灌溉列表响应模型
    """
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: list[FertilizationIrrigationResponse] = Field(..., description="记录列表")

    class Config:
        from_attributes = True
