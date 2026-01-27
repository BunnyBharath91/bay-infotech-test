"""
Railway-compatible KB ingestion script.
Uses the same connection approach as the running application.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.db.connection import init_db, close_db
import app.db.connection as db_conn
from app.db.models import KBDocument, KBChunk
from app.rag.ingestion import load_kb_directory, create_chunks
from app.rag.embeddings import get_embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def railway_ingest():
    """Ingest KB using Railway's connection context."""
    try:
        await init_db()
        
        if db_conn.async_session_maker is None:
            raise RuntimeError("Database session maker not initialized")
        
        # Load KB documents
        kb_dir = Path("/app/kb")
        if not kb_dir.exists():
            kb_dir = Path(__file__).parent / "kb"
        
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
        
        logger.info(f"KB ingestion completed! Processed {processed_docs} documents with {total_chunks} chunks")
        
    except Exception as e:
        logger.error(f"KB ingestion failed: {e}", exc_info=True)
        raise
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(railway_ingest())
