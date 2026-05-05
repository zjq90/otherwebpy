# -*- coding: utf-8 -*-
"""
数据库连接与会话管理
====================
提供异步数据库连接和会话管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # 生产环境设为False
    future=True
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """ORM模型基类"""
    pass


async def get_db():
    """
    数据库依赖注入函数
    用于FastAPI路由中获取数据库会话
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
