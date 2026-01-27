"""
SQLAlchemy database models.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Enum as SQLEnum, JSON, PickleType
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.connection import Base
from app.schemas.chat import Tier, Severity

# For SQLite compatibility, we'll store vectors as JSON arrays
# For PostgreSQL with pgvector, import conditionally
try:
    from pgvector.sqlalchemy import Vector
    USE_PGVECTOR = True
except ImportError:
    USE_PGVECTOR = False


class KBDocument(Base):
    """Knowledge Base document metadata."""
    __tablename__ = "kb_documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    version = Column(String, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    tags = Column(Text, default="[]")  # JSON-encoded list for compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunks = relationship("KBChunk", back_populates="document", cascade="all, delete-orphan")


class KBChunk(Base):
    """Knowledge Base document chunk with embedding."""
    __tablename__ = "kb_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kb_document_id = Column(String, ForeignKey("kb_documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    heading_path = Column(String)
    # Store embedding as JSON array for SQLite compatibility
    embedding = Column(JSON, nullable=True)  # Will store list of floats
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("KBDocument", back_populates="chunks")


class Conversation(Base):
    """User conversation session."""
    __tablename__ = "conversations"
    
    session_id = Column(String, primary_key=True)
    user_role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="conversation")
    guardrail_events = relationship("GuardrailEvent", back_populates="conversation")
    analytics_events = relationship("AnalyticsEvent", back_populates="conversation")


class Message(Base):
    """Conversation message."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("conversations.session_id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)  # JSON works with both SQLite and PostgreSQL
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Ticket(Base):
    """Support ticket."""
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True)  # INC-XXXX format
    session_id = Column(String, ForeignKey("conversations.session_id"), nullable=False)
    tier = Column(SQLEnum(Tier), nullable=False)
    severity = Column(SQLEnum(Severity), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="New")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tickets")


class GuardrailEvent(Base):
    """Guardrail activation event."""
    __tablename__ = "guardrail_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("conversations.session_id"), nullable=False)
    trigger_type = Column(String, nullable=False)
    blocked = Column(Boolean, nullable=False)
    user_message = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)  # JSON works with both SQLite and PostgreSQL
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="guardrail_events")


class AnalyticsEvent(Base):
    """Analytics event for tracking."""
    __tablename__ = "analytics_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    session_id = Column(String, ForeignKey("conversations.session_id"), nullable=True)
    meta_data = Column(JSON, default=dict)  # JSON works with both SQLite and PostgreSQL
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="analytics_events")
