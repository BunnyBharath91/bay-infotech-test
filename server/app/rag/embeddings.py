"""
Embedding service using Sentence Transformers.
Provides text embedding generation for RAG pipeline.

This module is designed to be **robust on environments where PyTorch /
sentence-transformers wheels are not available** (for example, Python 3.13).
In that case we fall back to a lightweight, deterministic, pure-Python
embedding implementation so that the API and tests can still run locally.
"""

import logging
import math
from typing import List
from functools import lru_cache

from app.config import get_settings

logger = logging.getLogger(__name__)

# Try to import SentenceTransformer, but gracefully degrade if it (or its
# PyTorch dependency) is unavailable for the current Python version.
try:  # pragma: no cover - import-time environment specific
    from sentence_transformers import SentenceTransformer  # type: ignore
    _HAS_SENTENCE_TRANSFORMERS = True
except Exception as exc:  # pragma: no cover - import-time environment specific
    SentenceTransformer = None  # type: ignore
    _HAS_SENTENCE_TRANSFORMERS = False
    logger.warning(
        "sentence-transformers could not be imported (%s). "
        "Falling back to simple pure-Python embeddings. "
        "This is expected on Python versions without PyTorch wheels.",
        exc,
    )


def _simple_embedding(text: str, dimension: int) -> List[float]:
    """
    Pure-Python fallback embedding.

    This is *not* semantically meaningful, but is:
    - deterministic
    - fast
    - has the requested dimensionality
    which is sufficient for local development and tests when real
    embedding models are unavailable.
    """
    vec = [0.0] * dimension
    if not text:
        return vec

    # Simple byte-wise hashing into a fixed-size vector
    data = text.encode("utf-8", errors="ignore")
    for i, b in enumerate(data):
        vec[i % dimension] += (b / 255.0)

    # L2-normalize for consistency
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self, model_name: str = None):
        """
        Initialize embedding service.

        Args:
            model_name: Name of the sentence-transformers model
        """
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

        self._use_fallback = not _HAS_SENTENCE_TRANSFORMERS
        self.model = None

        if not self._use_fallback:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                self.model = SentenceTransformer(self.model_name)  # type: ignore[arg-type]
                logger.info("Embedding model loaded successfully")
            except Exception as exc:  # pragma: no cover - environment specific
                logger.warning(
                    "Failed to load SentenceTransformer model '%s' (%s); "
                    "falling back to simple embeddings.",
                    self.model_name,
                    exc,
                )
                self._use_fallback = True

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            List of floats representing the embedding
        """
        if self._use_fallback or self.model is None:
            return _simple_embedding(text, self.dimension)

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of input texts

        Returns:
            List of embeddings
        """
        if self._use_fallback or self.model is None:
            return [_simple_embedding(t, self.dimension) for t in texts]

        embeddings = self.model.encode(
            texts, convert_to_numpy=True, show_progress_bar=True
        )
        return [emb.tolist() for emb in embeddings]

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


# Global embedding service instance
_embedding_service = None


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
