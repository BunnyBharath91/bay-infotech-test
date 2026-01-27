"""Full database reset"""
import asyncio
from sqlalchemy import text
from app.db.connection import init_db, close_db, get_engine
from app.db.models import Base

async def full_reset():
    await init_db()
    engine = get_engine()
    
    async with engine.begin() as conn:
        print("Dropping all tables...")
        await conn.run_sync(Base.metadata.drop_all)
        
        # Only enable pgvector for PostgreSQL
        db_url = str(engine.url)
        if 'postgresql' in db_url:
            print("Enabling pgvector extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        else:
            print("Using SQLite (no pgvector needed)...")
        
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        print("Database fully reset!")
    
    await close_db()

asyncio.run(full_reset())
