"""
数据库连接模块
创建SQLAlchemy数据库引擎、会话工厂和基础模型类
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings


# 创建SQLAlchemy引擎
# check_same_thread: False 是SQLite特定配置，允许多线程访问
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit=False: 不自动提交事务
# autoflush=False: 不自动刷新会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
# 所有数据模型都将继承这个类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    
    用于FastAPI的依赖注入系统，确保每个请求都获得独立的数据库会话，
    并在请求结束后自动关闭会话。
    
    Yields:
        Session: SQLAlchemy数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有在Base.metadata中注册的表
    """
    Base.metadata.create_all(bind=engine)
