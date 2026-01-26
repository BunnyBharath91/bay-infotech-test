"""
Unit tests for tier classification
"""
import pytest
from app.core.tiering import (
    classify_tier,
    Tier,
)


class TestTierClassification:
    """Test tier classification logic."""
    
    @pytest.mark.unit
    def test_tier_0_self_service(self):
        """Test TIER_0 classification for self-service issues."""
        # KB coverage exists, no previous attempts
        tier = classify_tier(
            issue_type="password_reset",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_0
    
    @pytest.mark.unit
    def test_tier_1_basic_issues(self):
        """Test TIER_1 classification for basic issues."""
        # Basic access issues
        tier = classify_tier(
            issue_type="password_reset",
            resolution_attempts=1,
            kb_coverage=False,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_1
        
        # Account locked
        tier = classify_tier(
            issue_type="account_locked",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_1
    
    @pytest.mark.unit
    def test_tier_2_technical_issues(self):
        """Test TIER_2 classification for technical issues."""
        # Lab crash
        tier = classify_tier(
            issue_type="lab_crash",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_2
        
        # DNS failure
        tier = classify_tier(
            issue_type="dns_failure",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_2
        
        # Container init failure
        tier = classify_tier(
            issue_type="container_init_failure",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_2
    
    @pytest.mark.unit
    def test_tier_3_critical_issues(self):
        """Test TIER_3 classification for critical issues."""
        # Kernel panic
        tier = classify_tier(
            issue_type="kernel_panic",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_3
        
        # Image bug
        tier = classify_tier(
            issue_type="image_bug",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_3
        
        # Systemic outage
        tier = classify_tier(
            issue_type="systemic_outage",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_3
    
    @pytest.mark.unit
    def test_escalation_on_repeated_failures(self):
        """Test that repeated failures trigger escalation."""
        # First attempt - TIER_0
        tier = classify_tier(
            issue_type="login_issue",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier == Tier.TIER_0
        
        # Second attempt - escalate to TIER_2
        tier = classify_tier(
            issue_type="login_issue",
            resolution_attempts=2,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        assert tier in [Tier.TIER_1, Tier.TIER_2]
    
    @pytest.mark.unit
    def test_no_kb_coverage_escalates(self):
        """Test that lack of KB coverage triggers escalation."""
        tier = classify_tier(
            issue_type="unknown_issue",
            resolution_attempts=0,
            kb_coverage=False,
            user_role="trainee",
            context={}
        )
        # Should escalate to at least TIER_1
        assert tier in [Tier.TIER_1, Tier.TIER_2]
    
    @pytest.mark.unit
    def test_multiple_users_affected(self):
        """Test that multiple affected users triggers higher tier."""
        tier = classify_tier(
            issue_type="lab_crash",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={"users_affected": 5}
        )
        # Should be at least TIER_2
        assert tier in [Tier.TIER_2, Tier.TIER_3]
    
    @pytest.mark.unit
    def test_deterministic_classification(self):
        """Test that same input produces same tier."""
        # Run classification multiple times
        results = []
        for _ in range(5):
            tier = classify_tier(
                issue_type="lab_crash",
                resolution_attempts=0,
                kb_coverage=True,
                user_role="trainee",
                context={}
            )
            results.append(tier)
        
        # All results should be identical
        assert len(set(results)) == 1
    
    @pytest.mark.unit
    def test_role_does_not_affect_tier(self):
        """Test that user role doesn't change tier classification."""
        # Same issue for different roles should have same tier
        tier_trainee = classify_tier(
            issue_type="lab_crash",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="trainee",
            context={}
        )
        
        tier_instructor = classify_tier(
            issue_type="lab_crash",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="instructor",
            context={}
        )
        
        tier_support = classify_tier(
            issue_type="lab_crash",
            resolution_attempts=0,
            kb_coverage=True,
            user_role="support_engineer",
            context={}
        )
        
        assert tier_trainee == tier_instructor == tier_support
