"""
Railway-compatible database initialization script.
Uses the same connection approach as the running application.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.connection import init_db, close_db, get_engine
import app.db.connection as db_conn
from app.db.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def railway_init():
    """Initialize database using Railway's connection context."""
    try:
        await init_db()
        engine = get_engine()
        
        if engine is None:
            raise RuntimeError("Failed to get database engine")
        
        if db_conn.async_session_maker is None:
            raise RuntimeError("Database session maker not initialized")
        
        # Use session maker (same as app startup)
        async with db_conn.async_session_maker() as session:
            conn = await session.connection()
            
            logger.info("Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
            # Enable pgvector for PostgreSQL
            db_url = str(engine.url)
            if 'postgresql' in db_url:
                logger.info("Enabling pgvector extension...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            logger.info("Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            
            await session.commit()
            logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        raise
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(railway_init())
