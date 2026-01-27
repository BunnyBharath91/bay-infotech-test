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
    
    # Prefer public URL if available (works better with Railway)
    # Convert postgresql:// to postgresql+asyncpg:// for asyncpg driver
    db_url = settings.DATABASE_PUBLIC_URL or settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not db_url.startswith("postgresql+asyncpg://"):
        # If it's already postgresql+asyncpg:// or sqlite, use as-is
        pass
    
    logger.info(f"Using database URL: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    
    # Configure connection pool for Railway
    # pool_pre_ping: Test connections before using (handles DNS resolution issues)
    # pool_size: Keep connections alive
    # max_overflow: Allow extra connections when needed
    engine = create_async_engine(
        db_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,  # Test connections before using them
        pool_size=5,  # Keep 5 connections alive
        max_overflow=10,  # Allow up to 10 extra connections
        pool_recycle=3600,  # Recycle connections after 1 hour
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Warm up the connection pool by making a test query
    # This helps establish the connection in Railway's network context
    try:
        async with async_session_maker() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            await session.commit()
        logger.info("Connection pool warmed up successfully")
    except Exception as e:
        logger.warning(f"Connection pool warm-up failed (may still work): {e}")
    
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
