"""
数据模型模块
包含所有数据库表的ORM模型定义
"""

# 导入各个模型
from backend.app.models.planting_plan import PlantingPlan
from backend.app.models.farm_operation import FarmOperation
from backend.app.models.fertilization_irrigation import FertilizationIrrigation
from backend.app.models.pest_disease_control import PestDiseaseControl

# 导出模型，方便外部使用
__all__ = [
    "PlantingPlan",
    "FarmOperation",
    "FertilizationIrrigation",
    "PestDiseaseControl"
]
