"""
应用配置模块
包含数据库连接配置、CORS配置等
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量读取配置，如果没有则使用默认值
    """
    
    # 项目名称
    PROJECT_NAME: str = "会员管理系统"
    # API版本
    API_V1_STR: str = "/api/v1"
    
    # SQLite数据库连接URL
    # 默认使用项目目录下的gym_system.db文件
    SQLITE_URL: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "gym_system.db"
    )
    DATABASE_URL: str = f"sqlite:///{SQLITE_URL}"
    
    # CORS配置 - 允许的前端地址
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    class Config:
        """Pydantic配置"""
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
