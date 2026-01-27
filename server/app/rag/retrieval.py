"""
RAG retrieval logic with vector similarity search.
"""

import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories import KBRepository
from app.db.models import KBChunk
from app.rag.embeddings import EmbeddingService
from app.rag.ranking import resolve_conflicts, filter_by_role
from app.schemas.chat import UserRole
from app.config import get_settings

logger = logging.getLogger(__name__)


async def retrieve_kb_chunks(
    query: str,
    user_role: UserRole,
    session: AsyncSession,
    embedding_service: EmbeddingService,
    top_k: int = None
) -> List[KBChunk]:
    """
    Retrieve relevant KB chunks for a query.
    
    Args:
        query: User query
        user_role: User's role for filtering
        session: Database session
        embedding_service: Embedding service
        top_k: Number of chunks to retrieve
    
    Returns:
        List of relevant KB chunks
    """
    settings = get_settings()
    top_k = top_k or settings.RAG_TOP_K
    
    logger.info(f"Retrieving KB chunks for query (top_k={top_k})")
    
    # Generate query embedding
    query_embedding = embedding_service.embed_text(query)
    
    # Search for similar chunks (retrieve extra for filtering)
    kb_repo = KBRepository(session)
    chunks = await kb_repo.search_chunks_by_embedding(
        query_embedding=query_embedding,
        top_k=top_k * 2  # Retrieve extra for filtering
    )
    
    logger.info(f"Retrieved {len(chunks)} chunks from vector search")
    
    if not chunks:
        logger.warning("No KB chunks found for query")
        return []
    
    # Apply role-based filtering
    filtered_chunks = filter_by_role(chunks, user_role)
    logger.info(f"After role filtering: {len(filtered_chunks)} chunks")
    
    # Resolve conflicts (prefer newer versions)
    resolved_chunks = resolve_conflicts(filtered_chunks)
    logger.info(f"After conflict resolution: {len(resolved_chunks)} chunks")
    
    # Return top_k chunks
    return resolved_chunks[:top_k]


async def check_kb_coverage(chunks: List[KBChunk], similarity_threshold: float = None) -> bool:
    """
    Check if retrieved KB chunks provide adequate coverage.
    
    Args:
        chunks: Retrieved KB chunks
        similarity_threshold: Minimum similarity threshold
    
    Returns:
        True if KB has adequate coverage
    """
    settings = get_settings()
    threshold = similarity_threshold or settings.RAG_SIMILARITY_THRESHOLD
    
    if not chunks:
        return False
    
    # For now, consider coverage adequate if we have at least one chunk
    # In production, you might want to check similarity scores
    return len(chunks) > 0


def format_kb_context(chunks: List[KBChunk]) -> str:
    """
    Format KB chunks into context string for LLM.
    
    Args:
        chunks: KB chunks
    
    Returns:
        Formatted context string
    """
    if not chunks:
        return ""
    
    context_parts = []
    for chunk in chunks:
        # Include document metadata and chunk content
        doc_id = chunk.kb_document_id
        heading = chunk.heading_path or "Content"
        text = chunk.chunk_text
        
        context_parts.append(
            f"[Document: {doc_id}]\n"
            f"[Section: {heading}]\n"
            f"{text}\n"
        )
    
    return "\n---\n".join(context_parts)
