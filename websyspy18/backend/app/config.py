"""
应用配置模块
包含数据库配置、API配置等
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    应用配置类
    使用pydantic_settings管理环境变量
    """
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./property_management.db"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "物业综合管理系统"
    VERSION: str = "1.0.0"
    
    # CORS配置 - 允许的前端域名
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-keep-it-safe-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建设置实例
settings = Settings()
