"""
数据库配置模块
负责数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# 数据库文件路径
DB_PATH = Path(__file__).parent.parent.parent / "data" / "property_management.db"

# 确保数据库目录存在
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLite 数据库URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建数据库引擎
# connect_args={'check_same_thread': False} 是SQLite的特殊配置
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # 设置为True可以显示SQL语句，便于调试
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有模型都将继承这个类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖项
    用于FastAPI的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    """
    Base.metadata.create_all(bind=engine)
