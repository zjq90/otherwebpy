"""
系统配置文件
包含数据库配置、认证配置、API配置等
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """系统配置类"""
    
    # 项目基本配置
    PROJECT_NAME: str = "车票监控与自动下单系统"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./ticket_system.db"
    
    # JWT认证配置
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时
    
    # 票务系统配置
    TICKET_API_BASE_URL: str = "https://kyfw.12306.cn"
    POLL_INTERVAL: float = 1.0  # 默认轮询间隔（秒）
    MAX_POLL_INTERVAL: float = 5.0  # 最大轮询间隔
    
    # HTTP请求配置
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    REFERER: str = "https://kyfw.12306.cn/otn/leftTicket/init"
    TIMEOUT: int = 10
    
    # 提醒配置
    ENABLE_SMS_ALERT: bool = False
    ENABLE_EMAIL_ALERT: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
