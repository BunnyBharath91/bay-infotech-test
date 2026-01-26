"""
Pydantic schemas for analytics and metrics.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, List


class TierMetrics(BaseModel):
    """Metrics by tier."""
    TIER_0: int = 0
    TIER_1: int = 0
    TIER_2: int = 0
    TIER_3: int = 0


class SeverityMetrics(BaseModel):
    """Metrics by severity."""
    LOW: int = 0
    MEDIUM: int = 0
    HIGH: int = 0
    CRITICAL: int = 0


class GuardrailMetrics(BaseModel):
    """Guardrail activation metrics."""
    total_activations: int = 0
    blocked_requests: int = 0
    by_type: Dict[str, int] = Field(default_factory=dict)


class MetricsSummary(BaseModel):
    """Summary metrics response."""
    deflection_rate: float = Field(..., description="Percentage of issues resolved at TIER_0")
    total_conversations: int
    total_tickets: int
    tickets_by_tier: TierMetrics
    tickets_by_severity: SeverityMetrics
    guardrail_activations: GuardrailMetrics
    escalation_count: int
    time_period: str = Field(..., description="Time period for metrics")


class TrendDataPoint(BaseModel):
    """Single data point in trend data."""
    timestamp: datetime
    value: int


class MetricsTrends(BaseModel):
    """Trend metrics response."""
    conversation_volume: List[TrendDataPoint]
    ticket_volume: List[TrendDataPoint]
    escalation_trend: List[TrendDataPoint]
    top_kb_references: List[Dict[str, any]]
    common_issue_categories: Dict[str, int]
