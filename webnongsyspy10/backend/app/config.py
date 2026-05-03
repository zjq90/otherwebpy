"""
配置模块
管理应用的配置参数，包括数据库连接、API配置等
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量或默认值读取配置参数
    """
    
    # 应用名称
    APP_NAME: str = "智慧农业管理系统"
    
    # 应用版本
    APP_VERSION: str = "1.0.0"
    
    # API前缀
    API_PREFIX: str = "/api/v1"
    
    # 数据库URL - SQLite数据库
    # 格式: sqlite:///数据库文件路径
    DATABASE_URL: str = "sqlite:///./agriculture.db"
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # 是否启用调试模式
    DEBUG: bool = True
    
    # 跨域配置
    CORS_ORIGINS: list = ["*"]  # 允许所有来源，生产环境应限制为特定域名
    
    # 静态文件目录
    STATIC_DIR: str = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static")
    
    # 模板文件目录
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "templates")
    
    # 高毒农药列表（用于预警）
    HIGH_TOXIC_PESTICIDES: list = [
        "甲胺磷", "甲基对硫磷", "对硫磷", "久效磷", "磷胺",
        "滴滴涕", "六六六", "林丹", "毒杀芬", "二溴氯丙烷",
        "杀虫脒", "二溴乙烷", "除草醚", "艾氏剂", "狄氏剂",
        "汞制剂", "砷类", "铅类", "敌枯双", "氟乙酰胺",
        "甘氟", "毒鼠强", "氟乙酸钠", "毒鼠硅"
    ]
    
    class Config:
        """
        Pydantic配置类
        """
        case_sensitive = True
        env_file = ".env"


# 创建全局配置实例
settings = Settings()
