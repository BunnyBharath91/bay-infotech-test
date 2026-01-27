"""
Pydantic schemas for chat API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from enum import Enum


class Tier(str, Enum):
    """Support tier classification."""
    TIER_0 = "TIER_0"  # Self-service via KB
    TIER_1 = "TIER_1"  # Human generalist
    TIER_2 = "TIER_2"  # Support Engineer
    TIER_3 = "TIER_3"  # Platform Engineering


class Severity(str, Enum):
    """Issue severity classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UserRole(str, Enum):
    """User role types."""
    TRAINEE = "trainee"
    INSTRUCTOR = "instructor"
    OPERATOR = "operator"
    SUPPORT_ENGINEER = "support_engineer"
    ADMIN = "admin"


class ChatContext(BaseModel):
    """Additional context for chat requests."""
    module: Optional[str] = None
    channel: Optional[str] = None
    environment: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request schema."""
    sessionId: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, description="User message")
    userRole: UserRole = Field(..., description="User role")
    context: Optional[ChatContext] = Field(default=None, description="Additional context")


class KBReference(BaseModel):
    """Knowledge base reference."""
    id: str = Field(..., description="KB document ID")
    title: str = Field(..., description="KB document title")
    version: Optional[str] = None
    relevance_score: Optional[float] = None


class GuardrailResult(BaseModel):
    """Guardrail check result."""
    blocked: bool = Field(..., description="Whether request was blocked")
    reason: Optional[str] = Field(None, description="Reason for blocking")
    trigger_type: Optional[str] = Field(None, description="Type of guardrail triggered")


class ChatResponse(BaseModel):
    """Chat response schema."""
    answer: str = Field(..., description="AI-generated answer")
    kbReferences: list[KBReference] = Field(default_factory=list, description="KB references used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    tier: Tier = Field(..., description="Support tier classification")
    severity: Severity = Field(..., description="Issue severity")
    needsEscalation: bool = Field(..., description="Whether escalation is needed")
    guardrail: GuardrailResult = Field(..., description="Guardrail check result")
    ticketId: Optional[str] = Field(None, description="Created ticket ID if escalated")
    sessionId: str = Field(..., description="Session identifier")
