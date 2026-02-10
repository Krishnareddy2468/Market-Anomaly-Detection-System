"""
Database Session Management
===========================
Async SQLAlchemy session factory and lifecycle management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Create async engine (PostgreSQL via asyncpg)
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,  # verify connections before use (handles RDS idle drops)
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


async def init_db() -> None:
    """
    Initialize database connection and create tables.
    
    Called during application startup.
    """
    logger.info("Initializing database connection", url=settings.DATABASE_URL[:50])
    
    async with engine.begin() as conn:
        # Import all models to ensure they're registered with Base.metadata
        from app.db.models import (  # noqa: F401
            TransactionModel,
            FeatureSnapshotModel,
            AlertModel,
            ModelScoreRecordModel,
            InvestigationModel,
            FeedbackModel,
            MetricsSnapshotModel,
        )
        
        # Create tables (for development/MVP)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialization complete")


async def close_db() -> None:
    """
    Close database connections.
    
    Called during application shutdown.
    """
    logger.info("Closing database connections")
    await engine.dispose()
    logger.info("Database connections closed")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes.
    
    Usage:
        @router.get("/")
        async def endpoint(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with get_db_session() as session:
        yield session
