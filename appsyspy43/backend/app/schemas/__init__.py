"""
数据验证模型模块
包含所有Pydantic数据验证模型，用于API请求和响应
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    UserLoginResponse,
    UserListResponse,
)
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleListResponse,
    VehicleLocationUpdate,
)
from app.schemas.transport_task import (
    TransportTaskCreate,
    TransportTaskUpdate,
    TransportTaskResponse,
    TransportTaskListResponse,
    TaskAssignRequest,
    TaskStatusUpdateRequest,
)
from app.schemas.location_record import (
    LocationRecordCreate,
    LocationRecordResponse,
    LocationRecordListResponse,
    LocationBatchCreate,
)
from app.schemas.task_update import (
    TaskUpdateCreate,
    TaskUpdateResponse,
    TaskUpdateListResponse,
)
from app.schemas.common import (
    ApiResponse,
    PaginatedResponse,
    Token,
    TokenData,
    MessageResponse,
)

# 导出所有模型，方便在其他地方导入
__all__ = [
    # 用户相关
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "UserLoginResponse",
    "UserListResponse",
    # 车辆相关
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    "VehicleListResponse",
    "VehicleLocationUpdate",
    # 运输任务相关
    "TransportTaskCreate",
    "TransportTaskUpdate",
    "TransportTaskResponse",
    "TransportTaskListResponse",
    "TaskAssignRequest",
    "TaskStatusUpdateRequest",
    # 位置记录相关
    "LocationRecordCreate",
    "LocationRecordResponse",
    "LocationRecordListResponse",
    "LocationBatchCreate",
    # 任务更新相关
    "TaskUpdateCreate",
    "TaskUpdateResponse",
    "TaskUpdateListResponse",
    # 通用
    "ApiResponse",
    "PaginatedResponse",
    "Token",
    "TokenData",
    "MessageResponse",
]
