"""
数据库配置文件
管理数据库连接和会话
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SQLite数据库路径
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'property_management.db')}"

# 创建数据库引擎
# check_same_thread: False 允许SQLite在多线程环境中使用
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建ORM模型基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
