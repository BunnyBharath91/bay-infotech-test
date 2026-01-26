"""
Pydantic schemas for ticket management.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

from app.schemas.chat import Tier, Severity


class TicketStatus(str, Enum):
    """Ticket status."""
    NEW = "New"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class TicketCreate(BaseModel):
    """Ticket creation schema."""
    session_id: str
    tier: Tier
    severity: Severity
    subject: str = Field(..., max_length=200)
    description: str


class TicketResponse(BaseModel):
    """Ticket response schema."""
    id: str
    session_id: str
    tier: Tier
    severity: Severity
    subject: str
    description: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """List of tickets response."""
    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int
