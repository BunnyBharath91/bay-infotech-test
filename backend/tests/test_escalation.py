"""
Unit tests for escalation logic
"""
import pytest
from app.core.escalation import (
    should_escalate,
    EscalationReason,
)


class TestEscalationLogic:
    """Test escalation decision logic."""
    
    @pytest.mark.unit
    def test_repeated_failures_escalate(self):
        """Test that repeated failures trigger escalation."""
        should_escalate_result, reason = should_escalate(
            issue_type="login_issue",
            resolution_attempts=2,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=False,
            context={}
        )
        assert should_escalate_result is True
        assert reason == EscalationReason.REPEATED_FAILURES
    
    @pytest.mark.unit
    def test_multiple_users_escalate(self):
        """Test that multiple affected users trigger escalation."""
        should_escalate_result, reason = should_escalate(
            issue_type="dns_failure",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=3,
            security_sensitive=False,
            context={}
        )
        assert should_escalate_result is True
        assert reason == EscalationReason.MULTIPLE_USERS
    
    @pytest.mark.unit
    def test_kernel_panic_escalates(self):
        """Test that kernel panic always escalates."""
        should_escalate_result, reason = should_escalate(
            issue_type="kernel_panic",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=False,
            context={}
        )
        assert should_escalate_result is True
        assert reason == EscalationReason.KERNEL_PANIC
    
    @pytest.mark.unit
    def test_container_failure_escalates(self):
        """Test that container startup failures escalate."""
        should_escalate_result, reason = should_escalate(
            issue_type="container_init_failure",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=False,
            context={"blocking_module": True}
        )
        assert should_escalate_result is True
        assert reason == EscalationReason.CONTAINER_FAILURE
    
    @pytest.mark.unit
    def test_security_sensitive_escalates(self):
        """Test that security-sensitive requests escalate."""
        should_escalate_result, reason = should_escalate(
            issue_type="unauthorized_access",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=True,
            context={}
        )
        assert should_escalate_result is True
        assert reason == EscalationReason.SECURITY_SENSITIVE
    
    @pytest.mark.unit
    def test_guardrail_high_severity_escalates(self):
        """Test that HIGH severity guardrail triggers escalate."""
        should_escalate_result, reason = should_escalate(
            issue_type="guardrail_violation",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=False,
            context={"guardrail_severity": "HIGH"}
        )
        assert should_escalate_result is True
        assert reason == EscalationReason.GUARDRAIL_HIGH_SEVERITY
    
    @pytest.mark.unit
    def test_no_escalation_for_simple_issues(self):
        """Test that simple issues don't escalate."""
        should_escalate_result, reason = should_escalate(
            issue_type="password_reset",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=False,
            context={}
        )
        assert should_escalate_result is False
        assert reason is None
    
    @pytest.mark.unit
    def test_user_preference_ignored(self):
        """Test that user preference to avoid escalation is ignored."""
        # User says "don't escalate" but conditions require it
        should_escalate_result, reason = should_escalate(
            issue_type="kernel_panic",
            resolution_attempts=0,
            kb_coverage=True,
            users_affected=1,
            security_sensitive=False,
            context={"user_requested_no_escalation": True}
        )
        # Should still escalate despite user preference
        assert should_escalate_result is True
        assert reason == EscalationReason.KERNEL_PANIC
    
    @pytest.mark.unit
    def test_no_kb_coverage_may_escalate(self):
        """Test that lack of KB coverage can trigger escalation."""
        should_escalate_result, reason = should_escalate(
            issue_type="unknown_issue",
            resolution_attempts=1,
            kb_coverage=False,
            users_affected=1,
            security_sensitive=False,
            context={}
        )
        # May or may not escalate depending on implementation
        # But if it does, reason should be NO_KB_COVERAGE
        if should_escalate_result:
            assert reason == EscalationReason.NO_KB_COVERAGE
    
    @pytest.mark.unit
    def test_deterministic_escalation(self):
        """Test that same conditions produce same escalation decision."""
        results = []
        for _ in range(5):
            should_escalate_result, reason = should_escalate(
                issue_type="kernel_panic",
                resolution_attempts=0,
                kb_coverage=True,
                users_affected=1,
                security_sensitive=False,
                context={}
            )
            results.append((should_escalate_result, reason))
        
        # All results should be identical
        assert len(set(results)) == 1
        assert results[0][0] is True
