"""
数据访问层模�?
封装所有数据库的增删改查操�?
"""

from app.crud.user import user_crud
from app.crud.role import role_crud
from app.crud.permission import permission_crud
from app.crud.operation_log import operation_log_crud

__all__ = [
    "user_crud",
    "role_crud",
    "permission_crud",
    "operation_log_crud",
]
