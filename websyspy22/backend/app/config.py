"""
系统配置模块
管理应用程序的环境变量和配置设置
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    应用程序配置类
    所有配置项都可以通过环境变量覆盖
    """
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./gym_system.db"
    
    # JWT/安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 短信服务配置（测试环境使用模拟发送）
    SMS_ENABLED: bool = False
    SMS_API_KEY: Optional[str] = None
    
    # 人脸识别配置（测试环境使用模拟）
    FACE_RECOGNITION_ENABLED: bool = False
    
    # 系统配置
    APP_NAME: str = "健身房会员管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 会员等级配置
    BRONZE_THRESHOLD: float = 0.0      # 青铜卡门槛
    SILVER_THRESHOLD: float = 5000.0   # 白银卡门槛
    GOLD_THRESHOLD: float = 20000.0    # 金卡门槛
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
