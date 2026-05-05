from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    应用程序配置类
    用于管理环境变量和应用配置
    """
    
    # 应用基本配置
    APP_NAME: str = "工业设备监测管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./equipment_monitoring.db"
    
    # CORS配置 - 允许的前端地址
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 创建设置实例
settings = Settings()
