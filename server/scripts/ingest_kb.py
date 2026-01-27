"""
KB ingestion script.
Loads KB files, generates embeddings, and stores in database.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.config import get_settings
from app.db.connection import init_db, get_session, engine
from app.db.models import Base
from app.db.repositories import KBRepository
from app.rag.ingestion import load_kb_directory, create_chunks
from app.rag.embeddings import get_embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ingest_kb():
    """Ingest KB files into database."""
    logger.info("Starting KB ingestion...")
    
    # Initialize database
    await init_db()
    
    # Get KB directory
    kb_dir = Path(__file__).parent.parent / "kb"
    if not kb_dir.exists():
        logger.error(f"KB directory not found: {kb_dir}")
        return
    
    # Load KB documents
    logger.info(f"Loading KB documents from: {kb_dir}")
    documents = load_kb_directory(kb_dir)
    logger.info(f"Loaded {len(documents)} documents")
    
    # Get embedding service
    embedding_service = get_embedding_service()
    
    # Process each document
    async for session in get_session():
        kb_repo = KBRepository(session)
        
        for document in documents:
            logger.info(f"Processing: {document.doc_id}")
            
            # Check if document already exists
            existing_doc = await kb_repo.get_document(document.doc_id)
            
            if existing_doc:
                logger.info(f"Document {document.doc_id} already exists, skipping...")
                continue
            
            # Create document record
            await kb_repo.create_document(
                doc_id=document.doc_id,
                title=document.title,
                version=document.version,
                last_updated=document.last_updated,
                tags=document.tags
            )
            
            # Create chunks
            chunks = create_chunks(document)
            logger.info(f"Created {len(chunks)} chunks for {document.doc_id}")
            
            # Generate embeddings for all chunks
            chunk_texts = [chunk.chunk_text for chunk in chunks]
            embeddings = embedding_service.embed_batch(chunk_texts)
            
            # Store chunks with embeddings
            for chunk, embedding in zip(chunks, embeddings):
                await kb_repo.create_chunk(
                    kb_document_id=chunk.kb_document_id,
                    chunk_text=chunk.chunk_text,
                    heading_path=chunk.heading_path,
                    embedding=embedding,
                    chunk_index=chunk.chunk_index
                )
            
            logger.info(f"Stored {len(chunks)} chunks for {document.doc_id}")
        
        await session.commit()
        logger.info("KB ingestion completed successfully!")
        break  # Exit after first session


if __name__ == "__main__":
    asyncio.run(ingest_kb())
