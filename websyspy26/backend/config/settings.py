"""
项目配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    项目配置类，使用pydantic-settings管理环境变量
    """
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./membership.db"
    
    # 应用配置
    APP_NAME: str = "会员管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # JWT配置（预留，用于后续认证功能）
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# 创建全局配置实例
settings = Settings()
