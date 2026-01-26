"""
Metrics and analytics API endpoints.
"""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.api.dependencies import get_db
from app.schemas.metrics import MetricsSummary, TierMetrics, SeverityMetrics, GuardrailMetrics
from app.db.models import Ticket, GuardrailEvent, AnalyticsEvent, Conversation
from app.schemas.chat import Tier, Severity

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
) -> MetricsSummary:
    """
    Get summary metrics for the specified time period.
    
    Args:
        hours: Number of hours to look back (default 24)
        db: Database session
    
    Returns:
        Metrics summary
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total conversations
    conv_result = await db.execute(
        select(func.count(Conversation.session_id))
        .where(Conversation.created_at >= since)
    )
    total_conversations = conv_result.scalar() or 0
    
    # Total tickets
    ticket_result = await db.execute(
        select(func.count(Ticket.id))
        .where(Ticket.created_at >= since)
    )
    total_tickets = ticket_result.scalar() or 0
    
    # Tickets by tier
    tier_result = await db.execute(
        select(Ticket.tier, func.count(Ticket.id))
        .where(Ticket.created_at >= since)
        .group_by(Ticket.tier)
    )
    tier_counts = {tier: count for tier, count in tier_result.all()}
    
    tickets_by_tier = TierMetrics(
        TIER_0=tier_counts.get(Tier.TIER_0, 0),
        TIER_1=tier_counts.get(Tier.TIER_1, 0),
        TIER_2=tier_counts.get(Tier.TIER_2, 0),
        TIER_3=tier_counts.get(Tier.TIER_3, 0)
    )
    
    # Tickets by severity
    severity_result = await db.execute(
        select(Ticket.severity, func.count(Ticket.id))
        .where(Ticket.created_at >= since)
        .group_by(Ticket.severity)
    )
    severity_counts = {severity: count for severity, count in severity_result.all()}
    
    tickets_by_severity = SeverityMetrics(
        LOW=severity_counts.get(Severity.LOW, 0),
        MEDIUM=severity_counts.get(Severity.MEDIUM, 0),
        HIGH=severity_counts.get(Severity.HIGH, 0),
        CRITICAL=severity_counts.get(Severity.CRITICAL, 0)
    )
    
    # Guardrail activations
    guardrail_result = await db.execute(
        select(func.count(GuardrailEvent.id))
        .where(GuardrailEvent.timestamp >= since)
    )
    total_guardrail_activations = guardrail_result.scalar() or 0
    
    blocked_result = await db.execute(
        select(func.count(GuardrailEvent.id))
        .where(GuardrailEvent.timestamp >= since)
        .where(GuardrailEvent.blocked == True)
    )
    blocked_requests = blocked_result.scalar() or 0
    
    type_result = await db.execute(
        select(GuardrailEvent.trigger_type, func.count(GuardrailEvent.id))
        .where(GuardrailEvent.timestamp >= since)
        .group_by(GuardrailEvent.trigger_type)
    )
    by_type = {trigger_type: count for trigger_type, count in type_result.all()}
    
    guardrail_metrics = GuardrailMetrics(
        total_activations=total_guardrail_activations,
        blocked_requests=blocked_requests,
        by_type=by_type
    )
    
    # Escalation count
    escalation_result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(AnalyticsEvent.timestamp >= since)
        .where(AnalyticsEvent.metadata['escalated'].astext == 'true')
    )
    escalation_count = escalation_result.scalar() or 0
    
    # Calculate deflection rate (TIER_0 / total conversations)
    tier_0_count = tickets_by_tier.TIER_0
    deflection_rate = (tier_0_count / total_conversations * 100) if total_conversations > 0 else 0.0
    
    return MetricsSummary(
        deflection_rate=round(deflection_rate, 2),
        total_conversations=total_conversations,
        total_tickets=total_tickets,
        tickets_by_tier=tickets_by_tier,
        tickets_by_severity=tickets_by_severity,
        guardrail_activations=guardrail_metrics,
        escalation_count=escalation_count,
        time_period=f"Last {hours} hours"
    )


@router.get("/metrics/trends")
async def get_metrics_trends(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trend metrics over time.
    
    Args:
        hours: Number of hours to look back
        db: Database session
    
    Returns:
        Trend data
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # For simplicity, return basic trend data
    # In production, you'd aggregate by time buckets
    
    return {
        "message": "Trend data endpoint - implement time-series aggregation as needed",
        "time_period": f"Last {hours} hours"
    }
