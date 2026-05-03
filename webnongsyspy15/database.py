"""
数据库连接模块
使用SQLAlchemy进行异步数据库操作
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL

# 创建异步数据库引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 生产环境可设置为False
    connect_args={"check_same_thread": False}  # SQLite专用
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """
    基础模型类
    所有数据库模型都继承此类
    """
    pass


async def init_db():
    """
    初始化数据库
    创建所有表
    """
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """
    获取数据库会话
    用于FastAPI依赖注入
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
