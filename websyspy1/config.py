"""
系统配置文件
包含数据库连接、JWT密钥等配置信息
"""
import os
from datetime import timedelta

# 项目基础路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite数据库配置
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'app.db')}"

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production-please-use-a-long-random-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 静态文件和模板配置
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# 分页配置
PAGE_SIZE = 10
