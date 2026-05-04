"""
系统配置文件
包含JWT密钥、数据库配置等全局配置
"""
import os
from datetime import timedelta
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    应用配置类
    从环境变量读取配置，也可以在.env文件中配置
    """
    
    # 应用名称
    APP_NAME: str = "健身俱乐部APP系统"
    
    # API版本
    API_VERSION: str = "v1"
    
    # 服务器地址
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gym_app.db')}"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-please"  # 生产环境请修改
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时有效期
    
    # CORS配置 - 允许的跨域源
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ])
    
    # 密码加密配置
    PASSWORD_HASH_SCHEME: str = "bcrypt"
    
    class Config:
        case_sensitive = True
        env_file = ".env"  # 支持从.env文件读取配置

# 创建全局配置实例
settings = Settings()
