from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    应用程序配置类
    使用pydantic-settings管理环境变量
    """
    
    # 应用名称
    APP_NAME: str = "农场管理系统"
    
    # 应用版本
    APP_VERSION: str = "1.0.0"
    
    # 数据库连接URL（SQLite）
    DATABASE_URL: str = "sqlite:///./farm_management.db"
    
    # 静态文件目录
    STATIC_DIR: str = "static"
    
    # 模板目录
    TEMPLATES_DIR: str = "templates"
    
    # 是否启用调试模式
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 跨域配置
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
