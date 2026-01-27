"""
Database connection management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

# Global engine and session maker
engine = None
async_session_maker = None


async def init_db():
    """Initialize database connection."""
    global engine, async_session_maker
    
    settings = get_settings()
    
    # Simple engine creation without extras
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("Database connection initialized")


async def close_db():
    """Close database connection."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Session error: {type(e).__name__}: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine():
    """Get database engine."""
    return engine
