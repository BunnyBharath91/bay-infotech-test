"""
Unit tests for severity classification
"""
import pytest
from app.core.severity import (
    classify_severity,
    Severity,
)


class TestSeverityClassification:
    """Test severity classification logic."""
    
    @pytest.mark.unit
    def test_critical_data_loss_risk(self):
        """Test CRITICAL severity for data loss risk."""
        severity = classify_severity(
            issue_type="lab_crash",
            users_affected=1,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=True
        )
        assert severity == Severity.CRITICAL
    
    @pytest.mark.unit
    def test_critical_security_sensitive(self):
        """Test CRITICAL severity for security-sensitive issues."""
        severity = classify_severity(
            issue_type="unauthorized_access",
            users_affected=1,
            blocking=False,
            security_sensitive=True,
            data_loss_risk=False
        )
        assert severity == Severity.CRITICAL
    
    @pytest.mark.unit
    def test_high_multiple_users(self):
        """Test HIGH severity for multiple affected users."""
        severity = classify_severity(
            issue_type="dns_failure",
            users_affected=6,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=False
        )
        assert severity == Severity.HIGH
    
    @pytest.mark.unit
    def test_high_systemic_outage(self):
        """Test HIGH severity for systemic outages."""
        severity = classify_severity(
            issue_type="systemic_outage",
            users_affected=1,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=False
        )
        assert severity == Severity.HIGH
    
    @pytest.mark.unit
    def test_medium_blocking_single_user(self):
        """Test MEDIUM severity for blocking issues affecting single user."""
        severity = classify_severity(
            issue_type="login_issue",
            users_affected=1,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=False
        )
        assert severity == Severity.MEDIUM
    
    @pytest.mark.unit
    def test_low_non_blocking(self):
        """Test LOW severity for non-blocking issues."""
        severity = classify_severity(
            issue_type="ui_glitch",
            users_affected=1,
            blocking=False,
            security_sensitive=False,
            data_loss_risk=False
        )
        assert severity == Severity.LOW
    
    @pytest.mark.unit
    def test_priority_order(self):
        """Test that severity priorities are correctly ordered."""
        # Data loss + security should still be CRITICAL
        severity = classify_severity(
            issue_type="breach",
            users_affected=10,
            blocking=True,
            security_sensitive=True,
            data_loss_risk=True
        )
        assert severity == Severity.CRITICAL
        
        # Multiple users + blocking should be HIGH
        severity = classify_severity(
            issue_type="outage",
            users_affected=10,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=False
        )
        assert severity == Severity.HIGH
    
    @pytest.mark.unit
    def test_deterministic_classification(self):
        """Test that same input produces same severity."""
        results = []
        for _ in range(5):
            severity = classify_severity(
                issue_type="lab_crash",
                users_affected=1,
                blocking=True,
                security_sensitive=False,
                data_loss_risk=True
            )
            results.append(severity)
        
        assert len(set(results)) == 1
        assert results[0] == Severity.CRITICAL
    
    @pytest.mark.unit
    def test_kernel_panic_severity(self):
        """Test severity for kernel panic scenarios."""
        severity = classify_severity(
            issue_type="kernel_panic",
            users_affected=1,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=True
        )
        assert severity == Severity.CRITICAL
    
    @pytest.mark.unit
    def test_container_failure_severity(self):
        """Test severity for container initialization failures."""
        severity = classify_severity(
            issue_type="container_init_failure",
            users_affected=1,
            blocking=True,
            security_sensitive=False,
            data_loss_risk=False
        )
        assert severity == Severity.MEDIUM
