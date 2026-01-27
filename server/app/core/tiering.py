"""
Tier classification - Deterministic rule-based logic.
NO LLM involvement - pure Python functions.
"""

import logging
from typing import Optional

from app.schemas.chat import Tier, UserRole

logger = logging.getLogger(__name__)


# Issue type to tier mapping
ISSUE_TYPE_TIER_MAP = {
    # TIER_0: Self-service via KB
    "general_question": Tier.TIER_0,
    "documentation_request": Tier.TIER_0,
    "how_to": Tier.TIER_0,
    
    # TIER_1: Human generalist
    "password_reset": Tier.TIER_1,
    "basic_access": Tier.TIER_1,
    "account_locked": Tier.TIER_1,
    "mfa_reset": Tier.TIER_1,
    
    # TIER_2: Support Engineer
    "lab_crash": Tier.TIER_2,
    "vm_unresponsive": Tier.TIER_2,
    "dns_failure": Tier.TIER_2,
    "container_init_failure": Tier.TIER_2,
    "network_connectivity": Tier.TIER_2,
    "environment_mapping": Tier.TIER_2,
    "authentication_loop": Tier.TIER_2,
    "time_drift": Tier.TIER_2,
    
    # TIER_3: Platform Engineering
    "kernel_panic": Tier.TIER_3,
    "image_bug": Tier.TIER_3,
    "systemic_outage": Tier.TIER_3,
    "infrastructure_failure": Tier.TIER_3,
}


def classify_tier(
    issue_type: Optional[str],
    resolution_attempts: int,
    kb_coverage: bool,
    user_role: UserRole,
    multiple_users_affected: bool = False,
    is_critical: bool = False
) -> Tier:
    """
    Classify support tier based on deterministic rules.
    
    Args:
        issue_type: Type of issue detected
        resolution_attempts: Number of previous resolution attempts
        kb_coverage: Whether KB has relevant content
        user_role: User's role
        multiple_users_affected: Whether multiple users report same issue
        is_critical: Whether issue is critical (kernel panic, data loss, etc.)
    
    Returns:
        Tier classification
    """
    # Critical issues always go to TIER_3
    if is_critical:
        logger.info(f"Critical issue detected, escalating to TIER_3")
        return Tier.TIER_3
    
    # Multiple users affected escalates to TIER_2 minimum
    if multiple_users_affected:
        logger.info(f"Multiple users affected, escalating to TIER_2 minimum")
        return Tier.TIER_2
    
    # Repeated failures (2+ attempts) escalate to TIER_2
    if resolution_attempts >= 2:
        logger.info(f"Repeated failures ({resolution_attempts} attempts), escalating to TIER_2")
        return Tier.TIER_2
    
    # If no KB coverage, escalate to TIER_1 (human needed)
    if not kb_coverage:
        logger.info(f"No KB coverage, escalating to TIER_1")
        return Tier.TIER_1
    
    # Use issue type mapping if available
    if issue_type and issue_type in ISSUE_TYPE_TIER_MAP:
        tier = ISSUE_TYPE_TIER_MAP[issue_type]
        logger.info(f"Issue type '{issue_type}' mapped to {tier}")
        return tier
    
    # Default: TIER_0 if KB coverage exists and first attempt
    if kb_coverage and resolution_attempts == 0:
        logger.info(f"KB coverage exists, first attempt, using TIER_0")
        return Tier.TIER_0
    
    # Fallback to TIER_1
    logger.info(f"No specific rule matched, defaulting to TIER_1")
    return Tier.TIER_1


def detect_issue_type(message: str, kb_chunks: list) -> Optional[str]:
    """
    Detect issue type from user message and KB chunks.
    Uses keyword matching - deterministic.
    
    Args:
        message: User message
        kb_chunks: Retrieved KB chunks
    
    Returns:
        Issue type string or None
    """
    message_lower = message.lower()
    
    # Critical issues (TIER_3)
    if any(keyword in message_lower for keyword in ["kernel panic", "kernel crash"]):
        return "kernel_panic"
    
    if any(keyword in message_lower for keyword in ["systemic", "all users", "entire platform"]):
        return "systemic_outage"
    
    # TIER_2 issues
    if any(keyword in message_lower for keyword in ["lab crash", "vm crash", "lab froze", "vm froze"]):
        return "lab_crash"
    
    if any(keyword in message_lower for keyword in ["container", "init failed", "startup.sh"]):
        return "container_init_failure"
    
    if any(keyword in message_lower for keyword in ["dns", "resolve", "domain"]):
        return "dns_failure"
    
    if any(keyword in message_lower for keyword in ["redirected", "login loop", "keep logging in"]):
        return "authentication_loop"
    
    if any(keyword in message_lower for keyword in ["wrong environment", "wrong lab", "incorrect environment"]):
        return "environment_mapping"
    
    if any(keyword in message_lower for keyword in ["time drift", "clock", "time sync"]):
        return "time_drift"
    
    if any(keyword in message_lower for keyword in ["network", "connectivity", "can't connect"]):
        return "network_connectivity"
    
    # TIER_1 issues
    if any(keyword in message_lower for keyword in ["password", "reset password", "forgot password"]):
        return "password_reset"
    
    if any(keyword in message_lower for keyword in ["mfa", "multi-factor", "authenticator"]):
        return "mfa_reset"
    
    if any(keyword in message_lower for keyword in ["locked out", "account locked"]):
        return "account_locked"
    
    if any(keyword in message_lower for keyword in ["access", "can't access", "unable to access"]):
        return "basic_access"
    
    # Check KB chunks for issue type hints
    if kb_chunks:
        for chunk in kb_chunks:
            chunk_text = getattr(chunk, 'chunk_text', '').lower()
            if "kernel panic" in chunk_text:
                return "kernel_panic"
            if "container" in chunk_text and "init" in chunk_text:
                return "container_init_failure"
    
    # Default to general question if no specific type detected
    return "general_question"
