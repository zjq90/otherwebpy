"""
数据库连接配置
使用SQLite数据库和SQLAlchemy ORM
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量读取配置，支持.env文件
    """
    SECRET_KEY: str = "your-secret-key-here-keep-it-safe"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时
    
    DATABASE_URL: str = "sqlite:///./concrete_quality.db"
    
    class Config:
        env_file = ".env"


settings = Settings()

# 创建数据库引擎
# SQLite需要设置check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
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


def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    from models.models import User, Material, MaterialInspection, ProductionFormula, ProductionRecord, QualityAlert, InspectionReport, FeedingRecord
    Base.metadata.create_all(bind=engine)
