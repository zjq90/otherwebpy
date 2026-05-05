"""
数据库连接模块
负责数据库连接、会话管理和初始化
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import get_settings
import os
import logging

logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 调试模式下打印SQL
    future=True
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """
    基础模型类
    所有模型都继承自此类
    """
    pass


async def get_db():
    """
    获取数据库会话依赖
    使用方式:
        db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库操作异常: {str(e)}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    # 确保数据目录存在
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    async with engine.begin() as conn:
        # 启用外键约束（SQLite特定）
        await conn.execute(text("PRAGMA foreign_keys=ON"))
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("数据库初始化完成")


async def execute_sql_file(sql_file_path: str):
    """
    执行SQL文件
    用于初始化数据
    """
    async with engine.begin() as conn:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（注意：这是一个简单的实现，可能无法处理复杂的SQL）
        # SQLite的executescript可以直接执行多个语句
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    await conn.execute(text(statement + ';'))
                except Exception as e:
                    logger.warning(f"执行SQL语句失败: {statement[:50]}... 错误: {str(e)}")
    
    logger.info(f"SQL文件执行完成: {sql_file_path}")
