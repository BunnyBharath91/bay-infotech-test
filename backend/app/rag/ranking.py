"""
KB conflict resolution and ranking logic.
"""

import logging
from typing import List, Dict
from collections import defaultdict
from packaging import version as version_parser

from app.db.models import KBChunk, KBDocument
from app.schemas.chat import UserRole
from app.core.guardrails import should_filter_kb_content

logger = logging.getLogger(__name__)


def resolve_conflicts(chunks: List[KBChunk]) -> List[KBChunk]:
    """
    Resolve conflicts when multiple KB documents cover the same topic.
    Prefers documents with higher version numbers or newer last_updated dates.
    
    Args:
        chunks: List of KB chunks
    
    Returns:
        List of chunks with conflicts resolved
    """
    if not chunks:
        return []
    
    # Group chunks by document ID
    chunks_by_doc: Dict[str, List[KBChunk]] = defaultdict(list)
    for chunk in chunks:
        chunks_by_doc[chunk.kb_document_id].append(chunk)
    
    # Get document metadata for each unique document
    doc_metadata: Dict[str, KBDocument] = {}
    for chunk in chunks:
        if chunk.kb_document_id not in doc_metadata:
            doc_metadata[chunk.kb_document_id] = chunk.document
    
    # Check for conflicting documents (same topic, different versions)
    # For now, we'll identify conflicts by similar document IDs or titles
    conflict_groups = identify_conflict_groups(doc_metadata)
    
    # For each conflict group, keep only the most authoritative document
    excluded_docs = set()
    for group in conflict_groups:
        if len(group) > 1:
            # Sort by version (descending) then by last_updated (descending)
            sorted_docs = sorted(
                group,
                key=lambda doc_id: (
                    parse_version(doc_metadata[doc_id].version),
                    doc_metadata[doc_id].last_updated
                ),
                reverse=True
            )
            
            # Keep the first (most authoritative), exclude others
            authoritative_doc = sorted_docs[0]
            for doc_id in sorted_docs[1:]:
                excluded_docs.add(doc_id)
                logger.info(
                    f"Excluding {doc_id} in favor of {authoritative_doc} "
                    f"(version {doc_metadata[authoritative_doc].version}, "
                    f"updated {doc_metadata[authoritative_doc].last_updated})"
                )
    
    # Filter out chunks from excluded documents
    resolved_chunks = [
        chunk for chunk in chunks
        if chunk.kb_document_id not in excluded_docs
    ]
    
    return resolved_chunks


def identify_conflict_groups(doc_metadata: Dict[str, KBDocument]) -> List[List[str]]:
    """
    Identify groups of documents that conflict with each other.
    
    Args:
        doc_metadata: Dictionary of document ID to KBDocument
    
    Returns:
        List of conflict groups (each group is a list of document IDs)
    """
    conflict_groups = []
    
    # Check for known conflicts based on document IDs
    # Example: kb-auth-policy-2023 and kb-auth-policy-2024 conflict
    auth_policy_docs = [
        doc_id for doc_id in doc_metadata.keys()
        if 'auth-policy' in doc_id or 'authentication-policy' in doc_id
    ]
    
    if len(auth_policy_docs) > 1:
        conflict_groups.append(auth_policy_docs)
        logger.info(f"Detected authentication policy conflict: {auth_policy_docs}")
    
    # Check for documents with similar titles
    title_groups: Dict[str, List[str]] = defaultdict(list)
    for doc_id, doc in doc_metadata.items():
        # Normalize title (remove version info, dates, etc.)
        normalized_title = normalize_title(doc.title)
        title_groups[normalized_title].append(doc_id)
    
    # Add groups with multiple documents
    for title, doc_ids in title_groups.items():
        if len(doc_ids) > 1 and doc_ids not in conflict_groups:
            conflict_groups.append(doc_ids)
            logger.info(f"Detected title-based conflict: {doc_ids}")
    
    return conflict_groups


def normalize_title(title: str) -> str:
    """
    Normalize document title for conflict detection.
    Removes version numbers, years, and other varying parts.
    
    Args:
        title: Original title
    
    Returns:
        Normalized title
    """
    import re
    
    # Remove version indicators
    title = re.sub(r'\s+v?\d+\.\d+', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+version\s+\d+\.\d+', '', title, flags=re.IGNORECASE)
    
    # Remove years
    title = re.sub(r'\s+20\d{2}', '', title)
    
    # Remove parenthetical notes
    title = re.sub(r'\([^)]+\)', '', title)
    
    # Remove "deprecated", "current", etc.
    title = re.sub(r'\s+(deprecated|current|old|new)', '', title, flags=re.IGNORECASE)
    
    # Normalize whitespace
    title = ' '.join(title.split())
    
    return title.strip().lower()


def parse_version(version_str: str) -> tuple:
    """
    Parse version string into comparable tuple.
    
    Args:
        version_str: Version string (e.g., "2.1", "1.0")
    
    Returns:
        Tuple for comparison
    """
    try:
        return version_parser.parse(version_str)
    except Exception:
        # Fallback to simple parsing
        parts = version_str.split('.')
        try:
            return tuple(int(p) for p in parts)
        except ValueError:
            return (0,)


def filter_by_role(chunks: List[KBChunk], user_role: UserRole) -> List[KBChunk]:
    """
    Filter KB chunks based on user role.
    Removes content that should not be shown to certain roles.
    
    Args:
        chunks: List of KB chunks
        user_role: User's role
    
    Returns:
        Filtered list of chunks
    """
    filtered = []
    
    for chunk in chunks:
        # Check if content should be filtered for this role
        if not should_filter_kb_content(chunk.chunk_text, user_role):
            filtered.append(chunk)
        else:
            logger.info(
                f"Filtered chunk from {chunk.kb_document_id} for role {user_role}"
            )
    
    return filtered
