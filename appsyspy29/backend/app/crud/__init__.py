"""
CRUD操作模块
包含所有数据库增删改查操作
"""
from .user_crud import (
    get_user_by_id,
    get_user_by_username,
    get_users,
    create_user,
    update_user,
    delete_user,
    authenticate_user
)
from .body_measurement_crud import (
    get_measurement_by_id,
    get_user_measurements,
    create_measurement,
    update_measurement,
    delete_measurement,
    get_measurement_stats,
    get_latest_measurement
)
from .exercise_crud import (
    get_exercise_by_id,
    get_exercises,
    get_exercises_by_category,
    create_exercise,
    update_exercise,
    delete_exercise,
    get_all_categories
)
from .training_log_crud import (
    get_training_log_by_id,
    get_user_training_logs,
    get_user_training_logs_by_date,
    create_training_log,
    update_training_log,
    delete_training_log,
    add_training_log_item,
    remove_training_log_item,
    get_training_log_with_items,
    get_user_monthly_stats
)
from .goal_crud import (
    get_goal_by_id,
    get_user_goals,
    get_active_goal,
    create_goal,
    update_goal,
    delete_goal,
    add_goal_progress,
    get_goal_progress_records,
    get_goal_with_details
)

__all__ = [
    # 用户相关
    "get_user_by_id",
    "get_user_by_username",
    "get_users",
    "create_user",
    "update_user",
    "delete_user",
    "authenticate_user",
    # 体测记录相关
    "get_measurement_by_id",
    "get_user_measurements",
    "create_measurement",
    "update_measurement",
    "delete_measurement",
    "get_measurement_stats",
    "get_latest_measurement",
    # 训练项目相关
    "get_exercise_by_id",
    "get_exercises",
    "get_exercises_by_category",
    "create_exercise",
    "update_exercise",
    "delete_exercise",
    "get_all_categories",
    # 训练日志相关
    "get_training_log_by_id",
    "get_user_training_logs",
    "get_user_training_logs_by_date",
    "create_training_log",
    "update_training_log",
    "delete_training_log",
    "add_training_log_item",
    "remove_training_log_item",
    "get_training_log_with_items",
    "get_user_monthly_stats",
    # 目标设定相关
    "get_goal_by_id",
    "get_user_goals",
    "get_active_goal",
    "create_goal",
    "update_goal",
    "delete_goal",
    "add_goal_progress",
    "get_goal_progress_records",
    "get_goal_with_details",
]
