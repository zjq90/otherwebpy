"""
数据模型模块
包含所有数据库表的模型定义
"""

from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.transport_task import TransportTask
from app.models.location_record import LocationRecord
from app.models.task_update import TaskUpdate

# 导出所有模型，方便在其他地方导入
__all__ = [
    "User",
    "Vehicle",
    "TransportTask",
    "LocationRecord",
    "TaskUpdate",
]
