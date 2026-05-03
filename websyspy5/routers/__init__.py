"""
API路由模块
包含所有FastAPI路由
"""
from routers import staff, device, access_record, attendance, test

__all__ = ["staff", "device", "access_record", "attendance", "test"]
