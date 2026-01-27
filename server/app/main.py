"""
FastAPI application entry point.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.routes import chat, tickets, metrics
from app.db.connection import init_db, close_db
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    await close_db()


# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception handler caught: {type(exc).__name__}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(tickets.router, prefix="/api", tags=["tickets"])
app.include_router(metrics.router, prefix="/api", tags=["metrics"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# ============================================================================
# TEMPORARY ADMIN ENDPOINTS FOR DATABASE INITIALIZATION
# Remove these after setup is complete
# ============================================================================

async def _init_database():
    """Internal function to initialize database."""
    from sqlalchemy import text
    from app.db.connection import get_engine
    import app.db.connection as db_conn
    from app.db.models import Base
    
    engine = get_engine()
    if engine is None:
        await init_db()
        engine = get_engine()
    
    if db_conn.async_session_maker is None:
        raise RuntimeError("Database session maker not initialized")
    
    # Drop tables in separate transaction
    async with db_conn.async_session_maker() as session:
        try:
            conn = await session.connection()
            logger.info("Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            await session.commit()
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            await session.rollback()
            raise
    
    # Enable pgvector extension in separate transaction (optional)
    db_url = str(engine.url)
    if 'postgresql' in db_url:
        async with db_conn.async_session_maker() as session:
            try:
                conn = await session.connection()
                logger.info("Attempting to enable pgvector extension...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await session.commit()
                logger.info("pgvector extension enabled successfully")
            except Exception as e:
                logger.warning(f"pgvector extension not available (will use JSON storage): {e}")
                await session.rollback()
    
    # Create tables in separate transaction
    async with db_conn.async_session_maker() as session:
        try:
            conn = await session.connection()
            logger.info("Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            await session.commit()
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            await session.rollback()
            raise
    
    return {"status": "success", "message": "Database initialized successfully"}


@app.get("/admin/init-db")
@app.post("/admin/init-db")
async def init_database():
    """Initialize database - TEMPORARY ENDPOINT FOR DEPLOYMENT (GET or POST)"""
    try:
        return await _init_database()
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


async def _ingest_knowledge_base():
    """Internal function to ingest knowledge base."""
    from pathlib import Path
    from sqlalchemy import text
    from app.db.models import KBDocument, KBChunk
    from app.db.connection import get_engine
    import app.db.connection as db_conn
    from app.rag.ingestion import load_kb_directory, create_chunks
    from app.rag.embeddings import get_embedding_service
    
    engine = get_engine()
    if engine is None:
        await init_db()
        engine = get_engine()
    
    if db_conn.async_session_maker is None:
        raise RuntimeError("Database session maker not initialized")
    
    # Load KB documents
    kb_dir = Path("/app/kb")
    if not kb_dir.exists():
        kb_dir = Path(__file__).parent.parent / "kb"
    
    documents = load_kb_directory(kb_dir)
    logger.info(f"Loaded {len(documents)} documents")
    
    # Get embedding service
    embedding_service = get_embedding_service()
    
    total_chunks = 0
    processed_docs = 0
    
    for document in documents:
        async with db_conn.async_session_maker() as session:
            try:
                logger.info(f"Processing: {document.doc_id}")
                
                # Check if document exists
                result = await session.execute(
                    text("SELECT id FROM kb_documents WHERE id = :id"),
                    {"id": document.doc_id}
                )
                exists = result.first()
                
                if exists:
                    logger.info(f"Document {document.doc_id} already exists, skipping")
                    continue
                
                # Create document
                kb_doc = KBDocument(
                    id=document.doc_id,
                    title=document.title,
                    version=document.version,
                    last_updated=document.last_updated,
                    tags=str(document.tags)
                )
                session.add(kb_doc)
                await session.flush()
                
                # Create chunks
                chunks = create_chunks(document)
                logger.info(f"Created {len(chunks)} chunks")
                
                # Generate embeddings
                chunk_texts = [chunk.chunk_text for chunk in chunks]
                embeddings = embedding_service.embed_batch(chunk_texts)
                
                # Store chunks
                for chunk, embedding in zip(chunks, embeddings):
                    kb_chunk = KBChunk(
                        kb_document_id=chunk.kb_document_id,
                        chunk_text=chunk.chunk_text,
                        heading_path=chunk.heading_path,
                        embedding=embedding,
                        chunk_index=chunk.chunk_index
                    )
                    session.add(kb_chunk)
                
                await session.commit()
                total_chunks += len(chunks)
                processed_docs += 1
                logger.info(f"Stored {len(chunks)} chunks for {document.doc_id}")
                
            except Exception as e:
                logger.error(f"Error processing {document.doc_id}: {e}")
                await session.rollback()
                raise
    
    return {
        "status": "success",
        "message": f"Ingested {processed_docs} documents with {total_chunks} chunks"
    }


@app.get("/admin/ingest-kb")
@app.post("/admin/ingest-kb")
async def ingest_knowledge_base():
    """Ingest knowledge base - TEMPORARY ENDPOINT FOR DEPLOYMENT (GET or POST)"""
    try:
        return await _ingest_knowledge_base()
    except Exception as e:
        logger.error(f"KB ingestion error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
