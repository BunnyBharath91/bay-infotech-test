"""
Escalation logic - Deterministic rule-based decisions.
NO LLM involvement - pure Python functions.
"""

import logging
from typing import Optional

from app.schemas.chat import Tier, Severity

logger = logging.getLogger(__name__)


def should_escalate(
    tier: Tier,
    severity: Severity,
    resolution_attempts: int,
    guardrail_blocked: bool,
    issue_type: Optional[str],
    kb_coverage: bool,
    user_requested_no_escalation: bool = False
) -> bool:
    """
    Determine if escalation is needed based on deterministic rules.
    
    IMPORTANT: User requests to avoid escalation are IGNORED per RULES.md.
    
    Args:
        tier: Classified tier
        severity: Classified severity
        resolution_attempts: Number of resolution attempts
        guardrail_blocked: Whether guardrail blocked the request
        issue_type: Detected issue type
        kb_coverage: Whether KB has coverage
        user_requested_no_escalation: User's preference (IGNORED)
    
    Returns:
        True if escalation is needed
    """
    # Rule 1: Critical severity always escalates
    if severity == Severity.CRITICAL:
        logger.info("Escalation required: CRITICAL severity")
        return True
    
    # Rule 2: Repeated failures (2+ attempts) require escalation
    if resolution_attempts >= 2:
        logger.info(f"Escalation required: Repeated failures ({resolution_attempts} attempts)")
        return True
    
    # Rule 3: Guardrail blocks with HIGH severity escalate
    if guardrail_blocked and severity in [Severity.HIGH, Severity.CRITICAL]:
        logger.info("Escalation required: Guardrail blocked with HIGH/CRITICAL severity")
        return True
    
    # Rule 4: No KB coverage requires human intervention
    if not kb_coverage:
        logger.info("Escalation required: No KB coverage")
        return True
    
    # Rule 5: Specific critical issue types always escalate
    critical_issue_types = [
        "kernel_panic",
        "systemic_outage",
        "infrastructure_failure",
        "image_bug"
    ]
    if issue_type in critical_issue_types:
        logger.info(f"Escalation required: Critical issue type '{issue_type}'")
        return True
    
    # Rule 6: Container startup failures blocking modules escalate
    if issue_type == "container_init_failure" and severity >= Severity.MEDIUM:
        logger.info("Escalation required: Container init failure blocking work")
        return True
    
    # Rule 7: TIER_2 and TIER_3 always escalate to human
    if tier in [Tier.TIER_2, Tier.TIER_3]:
        logger.info(f"Escalation required: Tier {tier} requires human support")
        return True
    
    # Rule 8: HIGH severity escalates
    if severity == Severity.HIGH:
        logger.info("Escalation required: HIGH severity")
        return True
    
    # Note: user_requested_no_escalation is intentionally ignored
    if user_requested_no_escalation:
        logger.warning("User requested no escalation, but request is IGNORED per policy")
    
    # No escalation needed
    logger.info("No escalation required")
    return False


def get_escalation_reason(
    tier: Tier,
    severity: Severity,
    resolution_attempts: int,
    guardrail_blocked: bool,
    issue_type: Optional[str],
    kb_coverage: bool
) -> Optional[str]:
    """
    Get human-readable reason for escalation.
    
    Args:
        tier: Classified tier
        severity: Classified severity
        resolution_attempts: Number of resolution attempts
        guardrail_blocked: Whether guardrail blocked
        issue_type: Detected issue type
        kb_coverage: Whether KB has coverage
    
    Returns:
        Escalation reason string or None
    """
    if severity == Severity.CRITICAL:
        return "Critical severity issue requires immediate attention from support team."
    
    if resolution_attempts >= 2:
        return f"Issue persists after {resolution_attempts} resolution attempts. Escalating to support engineer."
    
    if guardrail_blocked and severity in [Severity.HIGH, Severity.CRITICAL]:
        return "Security-sensitive request blocked. Support team has been notified."
    
    if not kb_coverage:
        return "This issue is not covered in the knowledge base. A support engineer will assist you."
    
    if issue_type in ["kernel_panic", "systemic_outage", "infrastructure_failure"]:
        return "Platform-level issue detected. Escalating to platform engineering team."
    
    if issue_type == "container_init_failure":
        return "Container initialization failure requires support engineer investigation."
    
    if tier in [Tier.TIER_2, Tier.TIER_3]:
        return f"This issue requires {tier.value} support. A ticket has been created."
    
    if severity == Severity.HIGH:
        return "High severity issue requires support engineer attention."
    
    return None


def detect_multiple_users_affected(message: str) -> bool:
    """
    Detect if multiple users are affected based on message content.
    
    Args:
        message: User message
    
    Returns:
        True if multiple users appear to be affected
    """
    message_lower = message.lower()
    
    multiple_user_indicators = [
        "everyone",
        "all users",
        "multiple users",
        "other users",
        "my team",
        "our team",
        "we all",
        "nobody can",
        "no one can",
    ]
    
    for indicator in multiple_user_indicators:
        if indicator in message_lower:
            logger.info(f"Multiple users indicator detected: {indicator}")
            return True
    
    return False
