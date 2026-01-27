"""Simple KB ingestion without connection caching issues"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

from app.config import get_settings
from app.db.models import KBDocument, KBChunk
from app.rag.ingestion import load_kb_directory, create_chunks
from app.rag.embeddings import get_embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simple_ingest():
    """Ingest KB files with fresh connection."""
    logger.info("Starting simple KB ingestion...")
    
    settings = get_settings()
    
    # Create fresh engine without pooling/caching
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=None,  # No connection pooling
        echo=False
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # Load KB documents
    kb_dir = Path(__file__).parent / "kb"
    documents = load_kb_directory(kb_dir)
    logger.info(f"Loaded {len(documents)} documents")
    
    # Get embedding service
    embedding_service = get_embedding_service()
    
    # Process each document
    for document in documents:
        async with async_session_maker() as session:
            try:
                logger.info(f"Processing: {document.doc_id}")
                
                # Check if exists
                result = await session.execute(
                    text("SELECT id FROM kb_documents WHERE id = :id"),
                    {"id": document.doc_id}
                )
                exists = result.first()
                
                if exists:
                    logger.info(f"Document {document.doc_id} exists, skipping")
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
                logger.info(f"Stored {len(chunks)} chunks for {document.doc_id}")
                
            except Exception as e:
                logger.error(f"Error processing {document.doc_id}: {e}")
                await session.rollback()
                raise
    
    await engine.dispose()
    logger.info("KB ingestion completed successfully!")

if __name__ == "__main__":
    asyncio.run(simple_ingest())
