"""
API路由模块
包含各个功能模块的API路由定义
"""

# 导入各个路由模块
from backend.app.routers.planting_plan import router as planting_plan_router
from backend.app.routers.farm_operation import router as farm_operation_router
from backend.app.routers.fertilization_irrigation import router as fertilization_irrigation_router
from backend.app.routers.pest_disease_control import router as pest_disease_control_router

# 导出路由
__all__ = [
    "planting_plan_router",
    "farm_operation_router",
    "fertilization_irrigation_router",
    "pest_disease_control_router",
]
