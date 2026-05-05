"""
配置模块 - 应用程序配置管理
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用程序配置类"""
    
    # 应用名称
    APP_NAME: str = "混凝土生产管理系统API"
    APP_VERSION: str = "1.0.0"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./concrete_prod.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production-please-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 偏差预警阈值配置（百分比）
    DEVIATION_WARNING_THRESHOLD: float = 5.0  # 超过5%触发警告
    DEVIATION_CRITICAL_THRESHOLD: float = 10.0  # 超过10%触发严重警告
    
    # 搅拌配置
    DEFAULT_MIXING_TIME_MINUTES: int = 30
    DEFAULT_ROTATION_SPEED: int = 30  # RPM
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
