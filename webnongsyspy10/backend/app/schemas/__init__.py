"""
数据验证模式（Schemas）模块
定义Pydantic模型，用于API请求和响应的数据验证
"""

# 导入各个模块的schemas
from backend.app.schemas.planting_plan import (
    PlantingPlanBase,
    PlantingPlanCreate,
    PlantingPlanUpdate,
    PlantingPlanResponse,
    PlanTypeEnum,
    PlanStatusEnum
)
from backend.app.schemas.farm_operation import (
    FarmOperationBase,
    FarmOperationCreate,
    FarmOperationUpdate,
    FarmOperationResponse,
    OperationTypeEnum,
    OperationStatusEnum
)
from backend.app.schemas.fertilization_irrigation import (
    FertilizationIrrigationBase,
    FertilizationIrrigationCreate,
    FertilizationIrrigationUpdate,
    FertilizationIrrigationResponse,
    FertilizerTypeEnum,
    IrrigationTypeEnum,
    WaterSourceEnum
)
from backend.app.schemas.pest_disease_control import (
    PestDiseaseControlBase,
    PestDiseaseControlCreate,
    PestDiseaseControlUpdate,
    PestDiseaseControlResponse,
    PestDiseaseTypeEnum,
    ControlMethodEnum,
    SeverityLevelEnum,
    TreatmentStatusEnum
)

# 导出
__all__ = [
    # 种植计划
    "PlantingPlanBase",
    "PlantingPlanCreate",
    "PlantingPlanUpdate",
    "PlantingPlanResponse",
    "PlanTypeEnum",
    "PlanStatusEnum",
    # 农事作业
    "FarmOperationBase",
    "FarmOperationCreate",
    "FarmOperationUpdate",
    "FarmOperationResponse",
    "OperationTypeEnum",
    "OperationStatusEnum",
    # 施肥灌溉
    "FertilizationIrrigationBase",
    "FertilizationIrrigationCreate",
    "FertilizationIrrigationUpdate",
    "FertilizationIrrigationResponse",
    "FertilizerTypeEnum",
    "IrrigationTypeEnum",
    "WaterSourceEnum",
    # 病虫害防治
    "PestDiseaseControlBase",
    "PestDiseaseControlCreate",
    "PestDiseaseControlUpdate",
    "PestDiseaseControlResponse",
    "PestDiseaseTypeEnum",
    "ControlMethodEnum",
    "SeverityLevelEnum",
    "TreatmentStatusEnum",
]
