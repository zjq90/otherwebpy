"""
配置文件模块
统一管理项目配置参数
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量读取配置，没有则使用默认值
    """
    
    # 项目基本配置
    PROJECT_NAME: str = "旧衣物回收App API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于FastAPI的旧衣物回收系统后端API"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/recycle.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 密码配置
    PASSWORD_HASH_ROUNDS: int = 12
    
    # 短信验证码配置（模拟）
    SMS_CODE_EXPIRE_MINUTES: int = 5
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 允许的文件类型
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # 跨域配置
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用lru_cache确保配置只加载一次
    """
    return Settings()


# 订单状态映射
ORDER_STATUS = {
    1: {"status": 1, "text": "待接单", "color": "#FF9800"},
    2: {"status": 2, "text": "待上门", "color": "#2196F3"},
    3: {"status": 3, "text": "回收中", "color": "#9C27B0"},
    4: {"status": 4, "text": "已完成", "color": "#4CAF50"},
    5: {"status": 5, "text": "已取消", "color": "#9E9E9E"},
}

# 积分交易类型
POINTS_TRANSACTION_TYPES = {
    "recycle": {"text": "回收奖励", "type": "income"},
    "invite": {"text": "邀请奖励", "type": "income"},
    "invited": {"text": "被邀请奖励", "type": "income"},
    "checkin": {"text": "每日签到", "type": "income"},
    "new_user": {"text": "新用户奖励", "type": "income"},
    "exchange": {"text": "积分兑换", "type": "expense"},
    "refund": {"text": "积分退还", "type": "income"},
    "adjust": {"text": "积分调整", "type": "other"},
}

# 兑换订单状态
EXCHANGE_ORDER_STATUS = {
    1: {"status": 1, "text": "待发货", "color": "#FF9800"},
    2: {"status": 2, "text": "已发货", "color": "#2196F3"},
    3: {"status": 3, "text": "已签收", "color": "#4CAF50"},
    4: {"status": 4, "text": "已取消", "color": "#9E9E9E"},
}

# 可预约时间段
DEFAULT_TIME_SLOTS = [
    "09:00-11:00",
    "11:00-13:00",
    "13:00-15:00",
    "15:00-17:00",
    "17:00-19:00",
    "19:00-21:00",
]
