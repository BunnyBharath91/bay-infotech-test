"""
Knowledge Base ingestion pipeline.
Parses markdown files, chunks by headings, extracts metadata, and generates embeddings.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import yaml

logger = logging.getLogger(__name__)


class KBDocument:
    """Represents a parsed KB document."""
    
    def __init__(
        self,
        doc_id: str,
        title: str,
        version: str,
        last_updated: datetime,
        tags: List[str],
        content: str
    ):
        self.doc_id = doc_id
        self.title = title
        self.version = version
        self.last_updated = last_updated
        self.tags = tags
        self.content = content


class KBChunkData:
    """Represents a chunk of KB content."""
    
    def __init__(
        self,
        kb_document_id: str,
        chunk_text: str,
        heading_path: str,
        chunk_index: int
    ):
        self.kb_document_id = kb_document_id
        self.chunk_text = chunk_text
        self.heading_path = heading_path
        self.chunk_index = chunk_index


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """
    Parse YAML frontmatter from markdown content.
    
    Args:
        content: Markdown content with frontmatter
    
    Returns:
        Tuple of (metadata dict, remaining content)
    """
    # Match YAML frontmatter between --- delimiters
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if not match:
        logger.warning("No frontmatter found in document")
        return {}, content
    
    frontmatter_text = match.group(1)
    remaining_content = content[match.end():]
    
    try:
        metadata = yaml.safe_load(frontmatter_text)
        return metadata, remaining_content
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse frontmatter: {e}")
        return {}, content


def parse_kb_file(file_path: Path) -> KBDocument:
    """
    Parse a KB markdown file.
    
    Args:
        file_path: Path to markdown file
    
    Returns:
        KBDocument object
    """
    logger.info(f"Parsing KB file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse frontmatter
    metadata, body = parse_frontmatter(content)
    
    # Extract metadata fields
    doc_id = metadata.get('id', file_path.stem)
    title = metadata.get('title', file_path.stem)
    version = str(metadata.get('version', '1.0'))
    
    # Parse last_updated date
    last_updated_str = metadata.get('last_updated', '')
    try:
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        logger.warning(f"Invalid date format for {file_path}, using current date")
        last_updated = datetime.utcnow()
    
    tags = metadata.get('tags', [])
    
    return KBDocument(
        doc_id=doc_id,
        title=title,
        version=version,
        last_updated=last_updated,
        tags=tags,
        content=body
    )


def chunk_by_headings(content: str, max_chunk_size: int = 1000) -> List[Tuple[str, str]]:
    """
    Chunk content by markdown headings.
    
    Args:
        content: Markdown content
        max_chunk_size: Maximum characters per chunk
    
    Returns:
        List of (heading_path, chunk_text) tuples
    """
    chunks = []
    
    # Split by headings (## and ###)
    heading_pattern = r'^(#{2,3})\s+(.+)$'
    lines = content.split('\n')
    
    current_heading_path = ""
    current_chunk = []
    current_size = 0
    
    for line in lines:
        heading_match = re.match(heading_pattern, line)
        
        if heading_match:
            # Save previous chunk if exists
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append((current_heading_path, chunk_text))
            
            # Start new chunk
            heading_level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            
            # Build heading path
            if heading_level == 2:
                current_heading_path = heading_text
            else:  # heading_level == 3
                # Keep parent heading and add sub-heading
                if ' > ' in current_heading_path:
                    parent = current_heading_path.split(' > ')[0]
                    current_heading_path = f"{parent} > {heading_text}"
                else:
                    current_heading_path = f"{current_heading_path} > {heading_text}"
            
            current_chunk = [line]
            current_size = len(line)
        else:
            # Add line to current chunk
            current_chunk.append(line)
            current_size += len(line) + 1  # +1 for newline
            
            # Split if chunk is too large
            if current_size > max_chunk_size and len(current_chunk) > 10:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append((current_heading_path, chunk_text))
                current_chunk = []
                current_size = 0
    
    # Save final chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append((current_heading_path, chunk_text))
    
    # If no chunks created (no headings), create one chunk with full content
    if not chunks and content.strip():
        chunks.append(("Introduction", content.strip()))
    
    logger.info(f"Created {len(chunks)} chunks")
    return chunks


def create_chunks(document: KBDocument) -> List[KBChunkData]:
    """
    Create chunks from a KB document.
    
    Args:
        document: KBDocument object
    
    Returns:
        List of KBChunkData objects
    """
    heading_chunks = chunk_by_headings(document.content)
    
    chunks = []
    for idx, (heading_path, chunk_text) in enumerate(heading_chunks):
        chunk = KBChunkData(
            kb_document_id=document.doc_id,
            chunk_text=chunk_text,
            heading_path=heading_path,
            chunk_index=idx
        )
        chunks.append(chunk)
    
    return chunks


def load_kb_directory(kb_dir: Path) -> List[KBDocument]:
    """
    Load all KB files from a directory.
    
    Args:
        kb_dir: Path to KB directory
    
    Returns:
        List of KBDocument objects
    """
    logger.info(f"Loading KB files from: {kb_dir}")
    
    documents = []
    md_files = sorted(kb_dir.glob("*.md"))
    
    for file_path in md_files:
        try:
            document = parse_kb_file(file_path)
            documents.append(document)
            logger.info(f"Loaded: {document.doc_id} (v{document.version})")
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
    
    logger.info(f"Loaded {len(documents)} KB documents")
    return documents
