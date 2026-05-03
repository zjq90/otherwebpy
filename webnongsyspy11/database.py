"""
数据库连接模块
使用SQLAlchemy ORM管理数据库连接和会话
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings, ensure_directories

# 确保数据目录存在
ensure_directories()

# 创建数据库引擎
# SQLite需要设置check_same_thread=False
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG  # 调试模式下输出SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建模型基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖注入函数
    在FastAPI路由中使用Depends(get_db)来获取数据库会话
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
    # 导入所有模型，确保它们被注册到Base.metadata中
    import models
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成，所有表已创建")
