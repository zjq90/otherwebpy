from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    应用程序配置类
    使用 pydantic-settings 管理环境变量
    """
    
    # 应用程序基本配置
    APP_NAME: str = "健身私教管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./gym_management.db"
    
    # CORS配置 - 允许的前端地址
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# 全局配置实例
settings = Settings()
