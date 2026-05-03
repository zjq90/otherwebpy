"""
系统配置模块
管理应用程序的配置参数，从环境变量或配置文件读取
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置类
    继承自BaseSettings，支持从环境变量读取配置
    """
    
    # 应用基本配置
    APP_NAME: str = "农产品溯源与认证管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./agriculture.db"
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # 二维码配置
    QRCODE_DIR: str = "./static/qrcodes"
    BASE_URL: str = "http://127.0.0.1:8000"
    
    # 认证提醒配置（天数）
    CERTIFICATE_REMINDER_DAYS: int = 30
    
    class Config:
        """Pydantic配置类"""
        case_sensitive = True
        env_file = ".env"


# 实例化配置对象
settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.QRCODE_DIR, exist_ok=True)
os.makedirs("./static/qrcodes", exist_ok=True)
