"""
工具函数模块
包含各种工具函数，包括安全认证、文件处理等
"""

from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    require_role,
    require_admin,
    require_dispatcher,
    require_driver,
    require_authenticated,
    pwd_context,
    oauth2_scheme,
)
from app.utils.helpers import (
    generate_task_no,
    calculate_distance,
    format_datetime,
    save_upload_file,
    get_file_url,
    calculate_estimated_arrival,
)

# 导出所有工具函数
__all__ = [
    # 安全相关
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "get_current_user",
    "require_role",
    "require_admin",
    "require_dispatcher",
    "require_driver",
    "require_authenticated",
    "pwd_context",
    "oauth2_scheme",
    # 辅助函数
    "generate_task_no",
    "calculate_distance",
    "format_datetime",
    "save_upload_file",
    "get_file_url",
    "calculate_estimated_arrival",
]
