from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./property_management.db")

engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        @event.listens_for(engine.sync_engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session_maker() as session:
        yield session
