"""
数据库连接模块
负责数据库连接、会话管理和基础模型
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings


# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # 生产环境设置为False
    future=True
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
    所有数据模型都继承此类
    """
    pass


async def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
