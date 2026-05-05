"""
API路由包
包含所有模块的API路由定义
"""
from .production import router as production_router
from .cost import router as cost_router
from .environment import router as environment_router

__all__ = ["production_router", "cost_router", "environment_router"]
