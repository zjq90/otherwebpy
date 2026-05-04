"""
数据模式模块
包含所有Pydantic模型，用于数据验证和序列�?
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    UserWithRoles,
)
from app.schemas.role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
)
from app.schemas.permission import (
    PermissionBase,
    PermissionCreate,
    PermissionUpdate,
    PermissionResponse,
)
from app.schemas.operation_log import (
    OperationLogBase,
    OperationLogCreate,
    OperationLogResponse,
    OperationLogQuery,
)
from app.schemas.token import (
    Token,
    TokenPayload,
)
from app.schemas.common import (
    ResponseModel,
    PaginatedResponse,
)

__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "UserWithRoles",
    "RoleBase", "RoleCreate", "RoleUpdate", "RoleResponse", "RoleWithPermissions",
    "PermissionBase", "PermissionCreate", "PermissionUpdate", "PermissionResponse",
    "OperationLogBase", "OperationLogCreate", "OperationLogResponse", "OperationLogQuery",
    "Token", "TokenPayload",
    "ResponseModel", "PaginatedResponse",
]
