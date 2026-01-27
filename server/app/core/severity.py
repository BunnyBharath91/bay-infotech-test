"""
Severity classification - Deterministic rule-based logic.
NO LLM involvement - pure Python functions.
"""

import logging
from typing import Optional

from app.schemas.chat import Severity

logger = logging.getLogger(__name__)


def classify_severity(
    issue_type: Optional[str],
    users_affected: int = 1,
    blocking: bool = False,
    security_sensitive: bool = False,
    data_loss_risk: bool = False,
    guardrail_triggered: bool = False,
    guardrail_severity: Optional[str] = None
) -> Severity:
    """
    Classify issue severity based on deterministic rules.
    
    Args:
        issue_type: Type of issue
        users_affected: Number of users affected
        blocking: Whether user is completely blocked
        security_sensitive: Whether issue involves security
        data_loss_risk: Whether there's risk of data loss
        guardrail_triggered: Whether a guardrail was triggered
        guardrail_severity: Severity from guardrail if triggered
    
    Returns:
        Severity classification
    """
    # CRITICAL: Data loss risk or security-sensitive
    if data_loss_risk:
        logger.info("Data loss risk detected, severity: CRITICAL")
        return Severity.CRITICAL
    
    if security_sensitive:
        logger.info("Security-sensitive issue detected, severity: CRITICAL")
        return Severity.CRITICAL
    
    # CRITICAL: Systemic outages
    if issue_type in ["systemic_outage", "infrastructure_failure"]:
        logger.info(f"Systemic issue type '{issue_type}', severity: CRITICAL")
        return Severity.CRITICAL
    
    # Use guardrail severity if provided
    if guardrail_triggered and guardrail_severity:
        if guardrail_severity == "CRITICAL":
            return Severity.CRITICAL
        elif guardrail_severity == "HIGH":
            return Severity.HIGH
    
    # HIGH: Multiple users affected (>5) or specific critical issue types
    if users_affected > 5:
        logger.info(f"Multiple users affected ({users_affected}), severity: HIGH")
        return Severity.HIGH
    
    if issue_type in ["kernel_panic", "image_bug", "lab_crash"]:
        logger.info(f"Critical issue type '{issue_type}', severity: HIGH")
        return Severity.HIGH
    
    # MEDIUM: User is blocked from work
    if blocking:
        logger.info("User is blocked, severity: MEDIUM")
        return Severity.MEDIUM
    
    # MEDIUM: Specific issue types that impact work
    if issue_type in [
        "container_init_failure",
        "authentication_loop",
        "environment_mapping",
        "vm_unresponsive"
    ]:
        logger.info(f"Blocking issue type '{issue_type}', severity: MEDIUM")
        return Severity.MEDIUM
    
    # LOW: Minor inconvenience, workaround available
    logger.info("No high-severity indicators, severity: LOW")
    return Severity.LOW


def is_security_sensitive(message: str, issue_type: Optional[str]) -> bool:
    """
    Determine if issue is security-sensitive.
    
    Args:
        message: User message
        issue_type: Detected issue type
    
    Returns:
        True if security-sensitive
    """
    message_lower = message.lower()
    
    # Security-related keywords
    security_keywords = [
        "disable logging",
        "bypass",
        "host access",
        "hypervisor",
        "privilege escalation",
        "root access",
        "unauthorized",
    ]
    
    for keyword in security_keywords:
        if keyword in message_lower:
            logger.info(f"Security-sensitive keyword detected: {keyword}")
            return True
    
    return False


def has_data_loss_risk(issue_type: Optional[str], message: str) -> bool:
    """
    Determine if issue has data loss risk.
    
    Args:
        issue_type: Detected issue type
        message: User message
    
    Returns:
        True if data loss risk exists
    """
    message_lower = message.lower()
    
    # Data loss indicators
    data_loss_keywords = [
        "lost work",
        "lost progress",
        "lost data",
        "data loss",
        "deleted",
        "corrupted",
        "can't recover",
    ]
    
    for keyword in data_loss_keywords:
        if keyword in message_lower:
            logger.info(f"Data loss risk keyword detected: {keyword}")
            return True
    
    # Certain issue types imply data loss risk
    if issue_type in ["lab_crash", "vm_unresponsive", "kernel_panic"]:
        if any(word in message_lower for word in ["work", "progress", "save"]):
            logger.info(f"Issue type '{issue_type}' with work/progress mention suggests data loss risk")
            return True
    
    return False
