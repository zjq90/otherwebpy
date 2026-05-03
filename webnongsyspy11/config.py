"""
系统配置文件
包含数据库配置、库存预警阈值等配置项
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    应用配置类
    使用pydantic-settings管理环境变量
    """
    
    # 应用名称
    APP_NAME: str = "农资管理系统"
    APP_VERSION: str = "1.0.0"
    
    # 数据库配置 - SQLite
    DATABASE_URL: str = "sqlite:///./data/agri_supply.db"
    
    # 库存预警阈值（百分比），默认为10%
    INVENTORY_ALERT_THRESHOLD: float = 0.10
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 静态文件和模板目录
    STATIC_DIR: str = os.path.join(os.path.dirname(__file__), "static")
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), "templates")
    
    # 数据目录（存放SQLite数据库文件）
    DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# 创建全局配置实例
settings = Settings()


# 确保必要的目录存在
def ensure_directories():
    """
    确保应用运行所需的目录都存在
    """
    directories = [
        settings.DATA_DIR,
        settings.STATIC_DIR,
        settings.TEMPLATES_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"创建目录: {directory}")
