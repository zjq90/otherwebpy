"""
系统配置模块
包含数据库连接、JWT密钥等核心配置
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    系统配置类
    从环境变量读取配置，未设置则使用默认值
    """
    
    # 应用名称
    APP_NAME: str = "多角色管理系统"
    
    # 应用版本
    APP_VERSION: str = "1.0.0"
    
    # API前缀
    API_PREFIX: str = "/api/v1"
    
    # 数据库URL (SQLite)
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # JWT密钥 (生产环境应使用强随机字符串)
    SECRET_KEY: str = "your-secret-key-change-in-production-2026"
    
    # JWT算法
    ALGORITHM: str = "HS256"
    
    # 访问令牌过期时间 (分钟)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # 验证码过期时间 (分钟)
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 5
    
    # 默认管理员账号
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    DEFAULT_ADMIN_PHONE: str = "13800138000"


# 全局配置实例
settings = Settings()
