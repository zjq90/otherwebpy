from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

"""
数据库配置模块
负责创建数据库引擎、会话工厂和基础模型类
"""

# 创建数据库引擎
# SQLite需要添加check_same_thread=False参数
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
# autocommit=False: 不自动提交
# autoflush=False: 不自动刷新
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类，所有ORM模型都需要继承这个类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖函数
    使用生成器模式，确保每次请求结束后关闭会话
    
    使用示例:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
