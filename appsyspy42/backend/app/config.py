"""
应用配置文件
包含数据库连接、JWT密钥等配置信息
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置类"""
    
    APP_NAME = "库存管理系统API"
    APP_VERSION = "1.0.0"
    API_PREFIX = "/api/v1"
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'inventory.db')}")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))
    
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
    ]


settings = Settings()
