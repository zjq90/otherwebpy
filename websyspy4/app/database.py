"""
数据库配置文件
使用SQLite作为数据库，SQLAlchemy作为ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite数据库URL
# 数据库文件名为rental_system.db，存放在项目根目录
SQLALCHEMY_DATABASE_URL = "sqlite:///./rental_system.db"

# 创建数据库引擎
# connect_args={"check_same_thread": False} 是SQLite特有的配置
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
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
