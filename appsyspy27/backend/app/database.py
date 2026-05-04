"""
数据库连接模块
使用SQLAlchemy实现数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# 创建数据库引擎
# SQLite需要设置check_same_thread为False以支持多线程
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG  # DEBUG模式下输出SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明性基类，所有模型都将继承此类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖项
    用于FastAPI的依赖注入，确保每次请求使用独立的数据库会话
    
    Yields:
        Session: SQLAlchemy数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有定义的表
    """
    Base.metadata.create_all(bind=engine)
