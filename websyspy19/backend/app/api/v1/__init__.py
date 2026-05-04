"""
API v1 模块
包含所有版�?的API路由
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.permissions import router as permissions_router
from app.api.v1.operation_logs import router as operation_logs_router
from app.api.v1.test import router as test_router


# 创建主API路由�?
api_router = APIRouter()

# 包含各个子路由器
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(roles_router, prefix="/roles", tags=["角色管理"])
api_router.include_router(permissions_router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(operation_logs_router, prefix="/operation-logs", tags=["操作日志"])
api_router.include_router(test_router, prefix="/test", tags=["测试功能"])
