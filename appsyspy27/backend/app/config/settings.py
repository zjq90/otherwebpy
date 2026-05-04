"""
系统配置模块
包含数据库连接、JWT密钥、API配置等全局配置项
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用程序全局配置类"""
    
    # 应用基本信息
    APP_NAME: str = "会员管理系统API"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./membership.db"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时过期
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 支付配置（模拟）
    WECHAT_PAY_ENABLED: bool = True
    ALIPAY_ENABLED: bool = True
    
    # 测试模式配置
    TEST_MODE: bool = True
    
    class Config:
        """Pydantic配置类"""
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
