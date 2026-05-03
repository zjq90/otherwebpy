"""
数据库连接模块
配置数据库连接、会话管理和基础模型
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine

from backend.app.config import settings


def get_database_engine() -> Engine:
    """
    创建数据库引擎
    
    返回:
        Engine: SQLAlchemy数据库引擎实例
    
    说明:
        - SQLite数据库需要启用check_same_thread=False
        - 生产环境可配置连接池参数
    """
    connect_args = {}
    
    # SQLite特殊配置
    if "sqlite" in settings.DATABASE_URL:
        # SQLite默认只允许同一线程使用连接，需要禁用此限制
        connect_args["check_same_thread"] = False
    
    # 创建数据库引擎
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        # 启用SQL语句日志（调试模式）
        echo=settings.DEBUG,
        # 连接池配置
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW
    )
    
    return engine


# 创建数据库引擎
engine = get_database_engine()

# 创建会话工厂
# autocommit=False: 不自动提交事务
# autoflush=False: 不自动刷新到数据库
# bind=engine: 绑定到数据库引擎
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建声明式基类
# 所有数据模型都需要继承此类
Base = declarative_base()


def get_db():
    """
    数据库会话依赖注入函数
    
    用于FastAPI路由中获取数据库会话
    使用yield实现上下文管理，确保会话正确关闭
    
    使用示例:
        @router.get("/")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: 数据库会话实例
    """
    db = SessionLocal()
    try:
        # 提供数据库会话给调用方
        yield db
    finally:
        # 无论是否发生异常，确保会话关闭
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表结构
    
    注意:
        - 此方法不会更新已存在的表结构
        - 生产环境应使用Alembic进行数据库迁移
    """
    # 导入所有模型，确保它们被注册到Base.metadata
    from backend.app.models import (
        planting_plan,
        farm_operation,
        fertilization_irrigation,
        pest_disease_control
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
