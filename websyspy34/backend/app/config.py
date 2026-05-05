import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "混凝土生产管理系统"
    APP_VERSION: str = "1.0.0"
    
    DATABASE_URL: Optional[str] = None
    
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

if not settings.DATABASE_URL:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    settings.DATABASE_URL = f"sqlite:///{os.path.join(os.path.dirname(BASE_DIR), 'concrete_production.db')}"
