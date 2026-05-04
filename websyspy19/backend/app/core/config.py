"""
应用配置模块
集中管理应用的所有配置项
"""

import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """
    应用配置�?
    从环境变量中读取配置，环境变量优先于默认�?
    """
    
    # 应用基本配置
    PROJECT_NAME: str = "权限管理系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配�?
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    # CORS 配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # 前端开发服务器
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        组装CORS源配�?
        支持从环境变量中读取逗号分隔的字符串
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 测试配置
    TEST_MODE: bool = False
    TEST_USER_COUNT: int = 10
    TEST_LOG_COUNT: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# 创建设置实例
settings = Settings()
