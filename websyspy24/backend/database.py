"""
数据库配置模块
负责数据库连接、会话管理和基础模型定义
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite数据库文件路径
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'gym_system.db')}"

# 创建数据库引擎
# check_same_thread=False 是SQLite特定的配置，允许多线程访问
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
# autocommit=False: 不自动提交事务
# autoflush=False: 不自动刷新会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有模型都将继承此类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    使用生成器模式，确保每次请求后关闭数据库连接
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    在应用启动时调用
    """
    Base.metadata.create_all(bind=engine)
