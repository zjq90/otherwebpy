from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    app_name: str = "生产数据管理系统"
    app_version: str = "1.0.0"
    debug: bool = True
    
    database_url: str = "sqlite:///./app.db"
    
    api_prefix: str = "/api/v1"
    
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
