"""
应用配置模块
使用pydantic-settings管理环境变量和配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置类
    管理所有环境变量和配置项
    """
    
    # 应用名称
    APP_NAME: str = "混凝土生产管理系统"
    
    # 应用版本
    VERSION: str = "1.0.0"
    
    # 调试模式
    DEBUG: bool = True
    
    # 数据库配置
    # SQLite数据库文件路径
    DATABASE_URL: str = "sqlite:///./concrete_management.db"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS配置（允许的前端地址）
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    # 环保监测阈值配置
    # 粉尘浓度阈值 (mg/m³)
    DUST_THRESHOLD: float = 0.15
    
    # 噪音阈值 (dB)
    NOISE_THRESHOLD: float = 85.0
    
    # 废水PH值阈值范围
    WASTEWATER_PH_MIN: float = 6.0
    WASTEWATER_PH_MAX: float = 9.0
    
    # 能耗单位成本 (元/千瓦时)
    ENERGY_COST_PER_KWH: float = 0.85
    
    class Config:
        """Pydantic配置类"""
        case_sensitive = True
        env_file = ".env"


# 创建全局配置实例
settings = Settings()
