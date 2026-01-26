"""
Repository pattern for data access layer.
Provides clean abstraction over database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.db.models import (
    Conversation, Message, Ticket, GuardrailEvent, 
    AnalyticsEvent, KBDocument, KBChunk
)
from app.schemas.chat import Tier, Severity


class ConversationRepository:
    """Repository for conversation operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_conversation(self, session_id: str, user_role: str) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(session_id=session_id, user_role=user_role)
        self.session.add(conversation)
        await self.session.flush()
        return conversation
    
    async def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        result = await self.session.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_conversation(self, session_id: str, user_role: str) -> Conversation:
        """Get existing conversation or create new one."""
        conversation = await self.get_conversation(session_id)
        if not conversation:
            conversation = await self.create_conversation(session_id, user_role)
        return conversation


class MessageRepository:
    """Repository for message operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: dict = None
    ) -> Message:
        """Create a new message."""
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.session.add(message)
        await self.session.flush()
        return message
    
    async def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Message]:
        """Get recent messages for a conversation."""
        result = await self.session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(desc(Message.timestamp))
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order


class TicketRepository:
    """Repository for ticket operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_ticket(
        self,
        session_id: str,
        tier: Tier,
        severity: Severity,
        subject: str,
        description: str
    ) -> Ticket:
        """Create a new ticket."""
        # Generate ticket ID
        ticket_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        
        ticket = Ticket(
            id=ticket_id,
            session_id=session_id,
            tier=tier,
            severity=severity,
            subject=subject,
            description=description
        )
        self.session.add(ticket)
        await self.session.flush()
        return ticket
    
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID."""
        result = await self.session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tickets_by_session(self, session_id: str) -> List[Ticket]:
        """Get all tickets for a session."""
        result = await self.session.execute(
            select(Ticket)
            .where(Ticket.session_id == session_id)
            .order_by(desc(Ticket.created_at))
        )
        return result.scalars().all()
    
    async def get_all_tickets(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Ticket], int]:
        """Get all tickets with pagination."""
        # Get total count
        count_result = await self.session.execute(select(func.count(Ticket.id)))
        total = count_result.scalar()
        
        # Get tickets
        result = await self.session.execute(
            select(Ticket)
            .order_by(desc(Ticket.created_at))
            .offset(skip)
            .limit(limit)
        )
        tickets = result.scalars().all()
        
        return tickets, total


class GuardrailEventRepository:
    """Repository for guardrail event operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_event(
        self,
        session_id: str,
        trigger_type: str,
        blocked: bool,
        user_message: str,
        metadata: dict = None
    ) -> GuardrailEvent:
        """Create a guardrail event."""
        event = GuardrailEvent(
            session_id=session_id,
            trigger_type=trigger_type,
            blocked=blocked,
            user_message=user_message,
            metadata=metadata or {}
        )
        self.session.add(event)
        await self.session.flush()
        return event
    
    async def get_recent_events(
        self, 
        hours: int = 24, 
        limit: int = 100
    ) -> List[GuardrailEvent]:
        """Get recent guardrail events."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(GuardrailEvent)
            .where(GuardrailEvent.timestamp >= since)
            .order_by(desc(GuardrailEvent.timestamp))
            .limit(limit)
        )
        return result.scalars().all()


class AnalyticsEventRepository:
    """Repository for analytics event operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_event(
        self,
        event_type: str,
        session_id: Optional[str] = None,
        metadata: dict = None
    ) -> AnalyticsEvent:
        """Create an analytics event."""
        event = AnalyticsEvent(
            event_type=event_type,
            session_id=session_id,
            metadata=metadata or {}
        )
        self.session.add(event)
        await self.session.flush()
        return event
    
    async def get_events_by_type(
        self, 
        event_type: str, 
        hours: int = 24
    ) -> List[AnalyticsEvent]:
        """Get events by type within time period."""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.session.execute(
            select(AnalyticsEvent)
            .where(
                and_(
                    AnalyticsEvent.event_type == event_type,
                    AnalyticsEvent.timestamp >= since
                )
            )
            .order_by(desc(AnalyticsEvent.timestamp))
        )
        return result.scalars().all()


class KBRepository:
    """Repository for Knowledge Base operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_document(
        self,
        doc_id: str,
        title: str,
        version: str,
        last_updated: datetime,
        tags: List[str]
    ) -> KBDocument:
        """Create a KB document."""
        document = KBDocument(
            id=doc_id,
            title=title,
            version=version,
            last_updated=last_updated,
            tags=tags
        )
        self.session.add(document)
        await self.session.flush()
        return document
    
    async def create_chunk(
        self,
        kb_document_id: str,
        chunk_text: str,
        heading_path: str,
        embedding: List[float],
        chunk_index: int
    ) -> KBChunk:
        """Create a KB chunk."""
        chunk = KBChunk(
            kb_document_id=kb_document_id,
            chunk_text=chunk_text,
            heading_path=heading_path,
            embedding=embedding,
            chunk_index=chunk_index
        )
        self.session.add(chunk)
        await self.session.flush()
        return chunk
    
    async def get_document(self, doc_id: str) -> Optional[KBDocument]:
        """Get KB document by ID."""
        result = await self.session.execute(
            select(KBDocument).where(KBDocument.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def search_chunks_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[KBChunk]:
        """Search KB chunks by embedding similarity."""
        # Use pgvector's cosine distance operator
        result = await self.session.execute(
            select(KBChunk)
            .order_by(KBChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return result.scalars().all()
    
    async def get_all_documents(self) -> List[KBDocument]:
        """Get all KB documents."""
        result = await self.session.execute(select(KBDocument))
        return result.scalars().all()
