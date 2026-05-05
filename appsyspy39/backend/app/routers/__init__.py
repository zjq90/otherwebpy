"""
Routers模块初始化文件
"""

from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router
from app.routers.formulas import router as formulas_router
from app.routers.feeding import router as feeding_router
from app.routers.mixing import router as mixing_router
from app.routers.test import router as test_router

__all__ = [
    "auth_router",
    "tasks_router",
    "formulas_router",
    "feeding_router",
    "mixing_router",
    "test_router"
]
