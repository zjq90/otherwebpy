"""
系统配置模块
包含数据库配置、JWT配置、API配置等
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """系统配置类"""
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./fitness_app.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # API配置
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "健身社交系统"
    VERSION: str = "1.0.0"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        """配置元类"""
        case_sensitive = True
        env_file = ".env"


# 创建全局配置实例
settings = Settings()
