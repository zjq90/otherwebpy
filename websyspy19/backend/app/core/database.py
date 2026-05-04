"""
数据库配置模�?
配置SQLAlchemy数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


# 创建数据库引�?
# SQLite需要设置check_same_thread为False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # 仅SQLite需�?
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """
    数据库依赖注入函�?
    用于在API路由中获取数据库会话
    
    用法示例:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
