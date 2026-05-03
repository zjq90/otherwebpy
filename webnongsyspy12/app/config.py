import os
from pydantic_settings import BaseSettings
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    应用配置类
    管理系统的所有配置参数，支持从环境变量读取
    """
    
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/agriculture.db"
    
    # 应用配置
    APP_NAME: str = "智慧农业监测系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 文件上传配置
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_VIDEO_TYPES: list = ["video/mp4", "video/avi", "video/mov"]
    
    # API配置
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "videos"), exist_ok=True)
