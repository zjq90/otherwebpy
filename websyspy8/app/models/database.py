"""
数据库连接管理模块
使用SQLAlchemy异步引擎管理数据库连接池
提供会话管理和数据库初始化功能
"""
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from loguru import logger

from app.config import settings
from app.models.models import Base


# ==================== 异步数据库引擎配置 ====================

def create_engine_with_config():
    """
    根据数据库类型创建引擎
    
    SQLite + aiosqlite 不支持连接池参数，需要特殊处理
    其他数据库(PostgreSQL/MySQL等)可以使用连接池配置
    """
    # 判断是否为SQLite数据库
    is_sqlite = "sqlite" in settings.DATABASE_URL.lower()
    
    if is_sqlite:
        # SQLite不支持pool_size, max_overflow等连接池参数
        # SQLite使用NullPool，每个连接都是独立的
        logger.info("检测到SQLite数据库，使用兼容配置")
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False}  # SQLite多线程支持
        )
    else:
        # 其他数据库使用连接池配置
        logger.info("使用连接池配置创建数据库引擎")
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=3600,
            pool_pre_ping=True,
        )


# 创建异步数据库引擎
engine = create_engine_with_config()

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ==================== 数据库会话管理 ====================

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话(依赖注入用)
    
    使用FastAPI依赖注入时，每个请求创建一个独立的会话
    请求结束后自动关闭会话
    
    Yields:
        AsyncSession: 异步数据库会话对象
        
    Example:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话异常: {str(e)}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    上下文管理器方式获取数据库会话
    
    适用于非依赖注入场景，如后台任务、脚本等
    
    Yields:
        AsyncSession: 异步数据库会话对象
        
    Example:
        async with get_session_context() as session:
            result = await session.execute(select(...))
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库上下文异常: {str(e)}")
            raise


# ==================== 数据库初始化 ====================

async def init_db() -> None:
    """
    初始化数据库
    
    创建所有定义的表结构
    注意: 这不会删除已存在的表
    
    使用方式:
        在应用启动时调用此函数初始化数据库
    """
    logger.info("开始初始化数据库...")
    
    async with engine.begin() as conn:
        # 创建所有表结构
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("数据库初始化完成!")


async def drop_all_tables() -> None:
    """
    删除所有表(慎用)
    
    用于开发环境重置数据库
    生产环境禁止使用
    """
    if not settings.DEBUG:
        logger.warning("非调试模式禁止删除表")
        return
    
    logger.warning("正在删除所有表...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.info("所有表已删除")


async def reset_db() -> None:
    """
    重置数据库
    
    删除所有表后重新创建
    仅用于开发环境
    """
    await drop_all_tables()
    await init_db()
    logger.info("数据库重置完成")
