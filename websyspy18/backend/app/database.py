"""
数据库连接和会话管理模块
使用SQLAlchemy作为ORM框架
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# 创建数据库引擎
# echo=True会打印SQL语句，生产环境建议设置为False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite需要的特殊配置
    echo=False
)

# 创建会话工厂
# autocommit=False: 不自动提交事务
# autoflush=False: 不自动刷新
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有数据模型都要继承这个类
Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入系统
    
    Yields:
        Session: 数据库会话实例
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    Base.metadata.create_all(bind=engine)
