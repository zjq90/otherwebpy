"""
农业报表系统配置文件
包含系统所有配置参数
"""

import os
from datetime import timedelta

# 项目基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'agriculture.db')}")

# 静态文件配置
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# API配置
API_PREFIX = "/api"
API_TITLE = "农业报表系统API"
API_DESCRIPTION = "农业生产、财务、环境报表管理系统"
API_VERSION = "1.0.0"

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "agriculture_report_system_secret_key_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CORS配置
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 数据配置
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
