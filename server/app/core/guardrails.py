"""
Guardrail engine - Rule-based content filtering and safety checks.
Implements pure Python pattern matching (no LLM involvement).
"""

import re
import logging
from typing import Optional, Tuple
from dataclasses import dataclass

from app.schemas.chat import UserRole

logger = logging.getLogger(__name__)


@dataclass
class GuardrailCheck:
    """Result of a guardrail check."""
    blocked: bool
    reason: Optional[str] = None
    trigger_type: Optional[str] = None
    severity: str = "MEDIUM"


# Forbidden action patterns (case-insensitive regex)
FORBIDDEN_PATTERNS = {
    "host_access": {
        "patterns": [
            r"access.*host.*machine",
            r"hypervisor.*access",
            r"ssh.*(?:to|into).*host",
            r"connect.*host.*system",
            r"host.*level.*access",
            r"escape.*(?:vm|container)",
        ],
        "message": "Access to host machines or hypervisors is not permitted. This request has been logged.",
        "severity": "HIGH"
    },
    "disable_logging": {
        "patterns": [
            r"disable.*log(?:ging)?",
            r"turn\s+off.*(?:log|monitor)",
            r"bypass.*log(?:ging)?",
            r"stop.*log(?:ging)?",
            r"hide.*activity",
            r"run.*quietly.*without.*log",
            r"suppress.*log",
        ],
        "message": "Logging and monitoring cannot be disabled. This is a mandatory security control.",
        "severity": "HIGH"
    },
    "kernel_debug": {
        "patterns": [
            r"kernel.*debug",
            r"driver.*modification",
            r"kernel.*module",
            r"modify.*kernel",
            r"kgdb",
            r"kernel.*panic.*debug",
        ],
        "message": "Kernel-level debugging and driver modification are not permitted for your role.",
        "severity": "HIGH"
    },
    "etc_hosts": {
        "patterns": [
            r"edit.*/etc/hosts",
            r"modify.*hosts.*file",
            r"change.*/etc/hosts",
            r"add.*(?:to|in).*/etc/hosts",
            r"update.*/etc/hosts",
        ],
        "message": "Modifying /etc/hosts is not permitted. Please contact support for DNS issues.",
        "severity": "MEDIUM"
    },
    "destructive": {
        "patterns": [
            r"reset.*all.*environment",
            r"delete.*all.*(?:lab|vm|environment)",
            r"destroy.*all",
            r"wipe.*all",
            r"remove.*all.*(?:user|lab)",
        ],
        "message": "Destructive system-wide operations are not permitted. Please contact your administrator.",
        "severity": "CRITICAL"
    },
}


# Role-based restrictions
ROLE_RESTRICTIONS = {
    UserRole.TRAINEE: {
        "forbidden_keywords": [
            "sudo", "root", "admin", "systemctl", "service",
            "iptables", "firewall", "selinux", "chmod 777"
        ],
        "message": "OS-level commands are not available for trainees. Please contact your instructor."
    },
    UserRole.INSTRUCTOR: {
        "forbidden_keywords": [
            "sudo", "root", "systemctl", "iptables", "firewall"
        ],
        "message": "OS-level system commands are not available for instructors. Please contact support."
    }
}


def check_guardrails(message: str, user_role: UserRole) -> GuardrailCheck:
    """
    Check if message violates any guardrails.
    Returns GuardrailCheck with blocked status and reason.
    
    This is a pure rule-based function - no LLM involvement.
    """
    message_lower = message.lower()
    
    # Check forbidden patterns
    for trigger_type, config in FORBIDDEN_PATTERNS.items():
        for pattern in config["patterns"]:
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.warning(
                    f"Guardrail triggered: {trigger_type} for role {user_role}",
                    extra={"trigger_type": trigger_type, "user_role": user_role}
                )
                return GuardrailCheck(
                    blocked=True,
                    reason=config["message"],
                    trigger_type=trigger_type,
                    severity=config["severity"]
                )
    
    # Check role-based restrictions
    if user_role in ROLE_RESTRICTIONS:
        restrictions = ROLE_RESTRICTIONS[user_role]
        for keyword in restrictions["forbidden_keywords"]:
            # Use word boundaries to avoid false positives
            if re.search(rf"\b{re.escape(keyword)}\b", message_lower):
                logger.warning(
                    f"Role restriction triggered: {keyword} for role {user_role}",
                    extra={"keyword": keyword, "user_role": user_role}
                )
                return GuardrailCheck(
                    blocked=True,
                    reason=restrictions["message"],
                    trigger_type="role_restriction",
                    severity="MEDIUM"
                )
    
    # No violations found
    return GuardrailCheck(blocked=False)


def should_filter_kb_content(kb_content: str, user_role: UserRole) -> bool:
    """
    Check if KB content should be filtered based on user role.
    Returns True if content should be blocked.
    """
    # Trainees and Instructors should not see OS-level commands
    if user_role in [UserRole.TRAINEE, UserRole.INSTRUCTOR]:
        sensitive_patterns = [
            r"sudo\s+",
            r"systemctl\s+",
            r"chmod\s+\d+",
            r"chown\s+",
            r"/etc/(?!hosts)",  # Block /etc/ paths except hosts (which is already blocked)
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, kb_content, re.IGNORECASE):
                return True
    
    return False


def sanitize_kb_content_for_role(kb_content: str, user_role: UserRole) -> str:
    """
    Sanitize KB content based on user role.
    Removes or redacts sensitive information.
    """
    if user_role in [UserRole.TRAINEE, UserRole.INSTRUCTOR]:
        # Remove command examples that contain sudo or system-level operations
        lines = kb_content.split('\n')
        sanitized_lines = []
        
        for line in lines:
            # Skip lines with sensitive commands
            if any(keyword in line.lower() for keyword in ['sudo', 'systemctl', 'iptables']):
                continue
            sanitized_lines.append(line)
        
        return '\n'.join(sanitized_lines)
    
    return kb_content
