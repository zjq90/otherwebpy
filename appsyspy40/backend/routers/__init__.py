"""
路由模块
包含所有API路由定义
"""
from routers.auth import router as auth_router
from routers.materials import router as materials_router
from routers.inspections import router as inspections_router
from routers.productions import router as productions_router
from routers.alerts import router as alerts_router
from routers.trace import router as trace_router
from routers.test import router as test_router
