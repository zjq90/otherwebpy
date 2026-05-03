"""
数据库连接和会话管理模块
负责创建数据库引擎、会话工厂和基础模型类
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
import os

# 确保数据库目录存在
db_dir = os.path.dirname(DATABASE_URL.replace('sqlite:///', ''))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)

# 创建数据库引擎
# check_same_thread: False 允许在不同线程中使用同一个连接
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit: False 不自动提交
# autoflush: False 不自动刷新
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基础模型类
# 所有的ORM模型都将继承自这个基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入
    使用yield实现上下文管理，确保会话在使用后被关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
