"""
路由模块
包含所有API路由
"""
from .user_router import router as user_router
from .body_measurement_router import router as body_measurement_router
from .exercise_router import router as exercise_router
from .training_log_router import router as training_log_router
from .goal_router import router as goal_router

__all__ = [
    "user_router",
    "body_measurement_router",
    "exercise_router",
    "training_log_router",
    "goal_router",
]
