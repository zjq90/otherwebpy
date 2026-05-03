"""
应用配置文件
包含所有配置项和常量
"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent

# 数据库路径
DATABASE_PATH = BASE_DIR / "database" / "cd_management.db"

# 数据库URL
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# JWT配置
# 实际生产环境应该从环境变量读取
SECRET_KEY = "your-secret-key-keep-it-safe-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 服务器配置
HOST = "127.0.0.1"
PORT = 8000
DEBUG = True

# 静态文件和模板路径
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# 分页配置
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# 用户角色
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# 借还状态
STATUS_BORROWED = "borrowed"
STATUS_RETURNED = "returned"
