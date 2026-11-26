"""
Database session management.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for getting database session outside of FastAPI dependencies."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


# --- added by fix script: drop duplicate index definitions before tables are created ---
from sqlalchemy import event as _sa_event


@_sa_event.listens_for(Base.metadata, "before_create")
def _dedupe_indexes(metadata, connection, **kw):
    seen = {}
    for table in metadata.sorted_tables:
        for idx in sorted(list(table.indexes), key=lambda i: i.name or ""):
            if idx.name is None:
                continue
            cols = tuple(c.name for c in idx.columns)
            if idx.name in seen:
                if seen[idx.name] == (table.name, cols):
                    table.indexes.discard(idx)
                    continue
                idx.name = f"{idx.name}_{table.name}"
            seen[idx.name] = (table.name, cols)
