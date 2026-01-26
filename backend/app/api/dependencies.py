"""
FastAPI dependencies for dependency injection.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connection import get_session
from app.llm.provider import get_llm_provider, LLMProvider
from app.rag.embeddings import get_embedding_service, EmbeddingService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in get_session():
        yield session


async def get_llm() -> LLMProvider:
    """Get LLM provider dependency."""
    return get_llm_provider()


async def get_embeddings() -> EmbeddingService:
    """Get embedding service dependency."""
    return get_embedding_service()
