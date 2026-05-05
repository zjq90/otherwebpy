"""
API路由模块
包含所有业务逻辑的API路由
"""

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.vehicles import router as vehicles_router
from app.routers.transport_tasks import router as transport_tasks_router
from app.routers.locations import router as locations_router
from app.routers.task_updates import router as task_updates_router
from app.routers.test import router as test_router

# 导出所有路由
__all__ = [
    "auth_router",
    "users_router",
    "vehicles_router",
    "transport_tasks_router",
    "locations_router",
    "task_updates_router",
    "test_router",
]
