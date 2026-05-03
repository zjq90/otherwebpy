"""
农事作业记录的数据验证模式
定义Pydantic模型，用于API请求和响应的数据验证
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class OperationTypeEnum(str, Enum):
    """
    作业类型枚举
    """
    SOWING = "播种"
    FERTILIZATION = "施肥"
    IRRIGATION = "灌溉"
    WEEDING = "除草"
    PEST_CONTROL = "病虫害防治"
    HARVEST = "收获"
    OTHER = "其他"


class OperationStatusEnum(str, Enum):
    """
    作业状态枚举
    """
    PLANNED = "计划中"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class FarmOperationBase(BaseModel):
    """
    农事作业记录基础模型
    """
    operation_name: str = Field(..., max_length=200, description="作业名称")
    operation_type: OperationTypeEnum = Field(..., description="作业类型")
    planned_date: Optional[date] = Field(None, description="计划作业日期")
    actual_date: date = Field(..., description="实际作业日期")
    crop_type: Optional[str] = Field(None, max_length=100, description="作物种类")
    plot_location: Optional[str] = Field(None, max_length=200, description="作业地块")
    operation_area: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="作业面积（亩）")
    operator: str = Field(..., max_length=100, description="操作人员")
    operator_contact: Optional[str] = Field(None, max_length=50, description="操作人员联系方式")
    scan_code_id: Optional[str] = Field(None, max_length=100, description="扫码记录ID（用于快速录入追溯）")
    is_app_entry: int = Field(default=0, ge=0, le=1, description="是否APP端录入：0-否，1-是")
    entry_device: Optional[str] = Field(None, max_length=200, description="录入设备信息")
    quantity: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=3, description="用量")
    quantity_unit: Optional[str] = Field(None, max_length=20, description="用量单位")
    operation_method: Optional[str] = Field(None, description="作业方法描述")
    tools_used: Optional[str] = Field(None, max_length=200, description="使用的工具/设备")
    weather_condition: Optional[str] = Field(None, max_length=100, description="作业时天气情况")
    status: OperationStatusEnum = Field(default=OperationStatusEnum.COMPLETED, description="作业状态")
    effect_assessment: Optional[str] = Field(None, description="作业效果评估")
    remarks: Optional[str] = Field(None, description="备注说明")
    photo_urls: Optional[str] = Field(None, description="现场照片URL")


class FarmOperationCreate(FarmOperationBase):
    """
    农事作业记录创建模型
    """
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    operation_code: str = Field(..., max_length=50, description="作业编号")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")


class FarmOperationUpdate(BaseModel):
    """
    农事作业记录更新模型
    """
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    operation_name: Optional[str] = Field(None, max_length=200, description="作业名称")
    operation_type: Optional[OperationTypeEnum] = Field(None, description="作业类型")
    planned_date: Optional[date] = Field(None, description="计划作业日期")
    actual_date: Optional[date] = Field(None, description="实际作业日期")
    crop_type: Optional[str] = Field(None, max_length=100, description="作物种类")
    plot_location: Optional[str] = Field(None, max_length=200, description="作业地块")
    operation_area: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="作业面积（亩）")
    operator: Optional[str] = Field(None, max_length=100, description="操作人员")
    operator_contact: Optional[str] = Field(None, max_length=50, description="操作人员联系方式")
    scan_code_id: Optional[str] = Field(None, max_length=100, description="扫码记录ID")
    is_app_entry: Optional[int] = Field(None, ge=0, le=1, description="是否APP端录入")
    entry_device: Optional[str] = Field(None, max_length=200, description="录入设备信息")
    quantity: Optional[Decimal] = Field(None, ge=0, max_digits=12, decimal_places=3, description="用量")
    quantity_unit: Optional[str] = Field(None, max_length=20, description="用量单位")
    operation_method: Optional[str] = Field(None, description="作业方法描述")
    tools_used: Optional[str] = Field(None, max_length=200, description="使用的工具/设备")
    weather_condition: Optional[str] = Field(None, max_length=100, description="作业时天气情况")
    status: Optional[OperationStatusEnum] = Field(None, description="作业状态")
    effect_assessment: Optional[str] = Field(None, description="作业效果评估")
    remarks: Optional[str] = Field(None, description="备注说明")
    photo_urls: Optional[str] = Field(None, description="现场照片URL")


class FarmOperationResponse(FarmOperationBase):
    """
    农事作业记录响应模型
    """
    id: int = Field(..., description="作业记录ID")
    planting_plan_id: Optional[int] = Field(None, description="关联种植计划ID")
    operation_code: str = Field(..., max_length=50, description="作业编号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")
    reviewed_by: Optional[str] = Field(None, max_length=100, description="审核人")
    reviewed_at: Optional[datetime] = Field(None, description="审核时间")

    class Config:
        from_attributes = True


class FarmOperationListResponse(BaseModel):
    """
    农事作业记录列表响应模型
    """
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: list[FarmOperationResponse] = Field(..., description="作业记录列表")

    class Config:
        from_attributes = True
