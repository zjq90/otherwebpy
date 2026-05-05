"""
配置模块
管理应用程序的所有配置项，包括数据库连接、JWT设置等
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
from pathlib import Path


# 项目根目录（基于config.py文件位置）
# config.py 位于 backend/app/config.py
# 所以根目录是 backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    应用程序配置类
    使用pydantic-settings从环境变量读取配置
    """
    
    # 应用基本配置
    APP_NAME: str = "运输管理系统API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置（使用绝对路径）
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'transport.db'}"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 文件上传配置（使用绝对路径）
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用lru_cache确保配置只被加载一次
    """
    return Settings()


# 导出配置实例
settings = get_settings()
