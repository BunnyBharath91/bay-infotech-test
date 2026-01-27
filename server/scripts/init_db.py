"""
Database initialization script.
Creates all tables and enables pgvector extension.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
import logging

from app.config import get_settings
from app.db.connection import init_db, get_engine
from app.db.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database schema."""
    logger.info("Initializing database...")
    
    # Initialize connection
    await init_db()
    engine = get_engine()
    
    # Enable pgvector extension
    async with engine.begin() as conn:
        logger.info("Enabling pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension enabled")
    
    # Create all tables
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())
