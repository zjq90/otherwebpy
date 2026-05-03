"""
系统配置文件
包含数据库连接、文件上传路径、JWT密钥等配置信息
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 数据库配置
DATABASE_URL = "sqlite:///./inventory.db"
# 启用外键支持（SQLite）
DATABASE_CONNECT_ARGS = {"check_same_thread": False}

# 文件上传配置
UPLOAD_DIR = BASE_DIR / "uploads"
PRODUCT_IMAGES_DIR = UPLOAD_DIR / "products"
EXCEL_EXPORT_DIR = UPLOAD_DIR / "exports"

# 创建必要的目录
for dir_path in [UPLOAD_DIR, PRODUCT_IMAGES_DIR, EXCEL_EXPORT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# JWT配置（用于用户认证）
SECRET_KEY = "your-secret-key-change-in-production-please"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时

# 分页配置
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# 图片上传配置
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
