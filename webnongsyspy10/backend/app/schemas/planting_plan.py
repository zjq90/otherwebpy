"""
种植计划管理的数据验证模式
定义Pydantic模型，用于API请求和响应的数据验证
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field


class PlanTypeEnum(str, Enum):
    """
    计划类型枚举
    """
    ANNUAL = "年度计划"
    QUARTERLY = "季度计划"
    MONTHLY = "月度计划"


class PlanStatusEnum(str, Enum):
    """
    计划状态枚举
    """
    DRAFT = "草稿"
    APPROVED = "已批准"
    IN_PROGRESS = "执行中"
    COMPLETED = "已完成"
    ADJUSTED = "已调整"
    CANCELLED = "已取消"


class PlantingPlanBase(BaseModel):
    """
    种植计划基础模型
    包含所有字段的基础定义
    """
    plan_name: str = Field(..., max_length=200, description="计划名称")
    plan_type: PlanTypeEnum = Field(..., description="计划类型：年度/季度/月度")
    year: int = Field(..., ge=2000, le=2100, description="计划年度")
    quarter: Optional[int] = Field(None, ge=1, le=4, description="季度：1-4，年度计划可为空")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份：1-12，季度计划可为空")
    crop_type: str = Field(..., max_length=100, description="作物种类")
    crop_variety: Optional[str] = Field(None, max_length=100, description="作物品种")
    planting_area: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2, description="种植面积（亩）")
    sowing_date: date = Field(..., description="预计播种时间")
    expected_harvest_date: date = Field(..., description="预计收获时间")
    actual_harvest_date: Optional[date] = Field(None, description="实际收获时间")
    target_yield_per_mu: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="目标产量（公斤/亩）")
    actual_yield_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2, description="实际产量（公斤/亩）")
    location: Optional[str] = Field(None, max_length=200, description="种植地点/地块")
    status: PlanStatusEnum = Field(default=PlanStatusEnum.DRAFT, description="计划状态")
    progress: Decimal = Field(default=Decimal("0.00"), ge=0, le=100, max_digits=5, decimal_places=2, description="执行进度（百分比）")
    responsible_person: Optional[str] = Field(None, max_length=100, description="责任人")
    remarks: Optional[str] = Field(None, description="备注说明")


class PlantingPlanCreate(PlantingPlanBase):
    """
    种植计划创建模型
    用于创建新的种植计划请求
    """
    plan_code: str = Field(..., max_length=50, description="计划编号")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")


class PlantingPlanUpdate(BaseModel):
    """
    种植计划更新模型
    用于更新现有种植计划请求
    所有字段都是可选的，允许部分更新
    """
    plan_name: Optional[str] = Field(None, max_length=200, description="计划名称")
    plan_type: Optional[PlanTypeEnum] = Field(None, description="计划类型：年度/季度/月度")
    year: Optional[int] = Field(None, ge=2000, le=2100, description="计划年度")
    quarter: Optional[int] = Field(None, ge=1, le=4, description="季度：1-4，年度计划可为空")
    month: Optional[int] = Field(None, ge=1, le=12, description="月份：1-12，季度计划可为空")
    crop_type: Optional[str] = Field(None, max_length=100, description="作物种类")
    crop_variety: Optional[str] = Field(None, max_length=100, description="作物品种")
    planting_area: Optional[Decimal] = Field(None, gt=0, max_digits=10, decimal_places=2, description="种植面积（亩）")
    sowing_date: Optional[date] = Field(None, description="预计播种时间")
    expected_harvest_date: Optional[date] = Field(None, description="预计收获时间")
    actual_harvest_date: Optional[date] = Field(None, description="实际收获时间")
    target_yield_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2, description="目标产量（公斤/亩）")
    actual_yield_per_mu: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2, description="实际产量（公斤/亩）")
    location: Optional[str] = Field(None, max_length=200, description="种植地点/地块")
    status: Optional[PlanStatusEnum] = Field(None, description="计划状态")
    progress: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2, description="执行进度（百分比）")
    responsible_person: Optional[str] = Field(None, max_length=100, description="责任人")
    remarks: Optional[str] = Field(None, description="备注说明")


class PlantingPlanResponse(PlantingPlanBase):
    """
    种植计划响应模型
    用于API返回的种植计划数据
    """
    id: int = Field(..., description="种植计划ID")
    plan_code: str = Field(..., max_length=50, description="计划编号")
    target_total_yield: Optional[Decimal] = Field(None, max_digits=12, decimal_places=2, description="目标总产量（公斤）")
    actual_total_yield: Optional[Decimal] = Field(None, max_digits=12, decimal_places=2, description="实际总产量（公斤）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")

    class Config:
        """
        Pydantic配置
        """
        from_attributes = True  # 支持从ORM模型读取
        json_schema_extra = {
            "example": {
                "id": 1,
                "plan_code": "PP20240001",
                "plan_name": "2024年水稻年度种植计划",
                "plan_type": "年度计划",
                "year": 2024,
                "quarter": None,
                "month": None,
                "crop_type": "水稻",
                "crop_variety": "杂交稻",
                "planting_area": 50.50,
                "sowing_date": "2024-04-15",
                "expected_harvest_date": "2024-09-20",
                "actual_harvest_date": "2024-09-25",
                "target_yield_per_mu": 600.00,
                "target_total_yield": 30300.00,
                "actual_yield_per_mu": 650.00,
                "actual_total_yield": 32825.00,
                "location": "东区一号田",
                "status": "已完成",
                "progress": 100.00,
                "responsible_person": "张三",
                "remarks": "2024年水稻种植计划",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-09-25T15:00:00",
                "created_by": "系统管理员"
            }
        }


class PlantingPlanListResponse(BaseModel):
    """
    种植计划列表响应模型
    用于分页查询的响应
    """
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: list[PlantingPlanResponse] = Field(..., description="种植计划列表")

    class Config:
        from_attributes = True
