"""
数据库连接和会话管理模块
处理SQLAlchemy的引擎、会话和基础模型创建
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 创建SQLAlchemy引擎
# check_same_thread=False 是SQLite特定配置，允许在不同线程中使用同一连接
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit=False: 不自动提交事务
# autoflush=False: 不自动刷新会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类，所有数据库模型都将继承此类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入，确保每个请求都有独立的数据库会话
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # 确保会话在使用后关闭
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表结构（如果不存在）
    """
    # 导入所有模型，确保Base.metadata包含所有表定义
    from app import models
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
