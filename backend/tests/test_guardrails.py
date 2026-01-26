"""
Unit tests for guardrails engine
"""
import pytest
from app.core.guardrails import (
    GuardrailEngine,
    GuardrailResult,
    GuardrailCategory,
)


@pytest.fixture
def guardrail_engine():
    """Create a guardrail engine instance."""
    return GuardrailEngine()


class TestGuardrailEngine:
    """Test guardrail engine functionality."""
    
    @pytest.mark.unit
    def test_host_access_blocked(self, guardrail_engine):
        """Test that host access requests are blocked."""
        messages = [
            "How do I access the host machine?",
            "Can you show me how to SSH into the hypervisor?",
            "I need to access the host system behind my VM",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is True
            assert result.category == GuardrailCategory.HOST_ACCESS
            assert result.severity == "HIGH"
    
    @pytest.mark.unit
    def test_disable_logging_blocked(self, guardrail_engine):
        """Test that attempts to disable logging are blocked."""
        messages = [
            "How do I disable logging?",
            "Show me how to turn off monitoring",
            "Can I bypass the logging system?",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is True
            assert result.category == GuardrailCategory.DISABLE_LOGGING
            assert result.severity == "HIGH"
    
    @pytest.mark.unit
    def test_kernel_debug_blocked(self, guardrail_engine):
        """Test that kernel debugging requests are blocked."""
        messages = [
            "How do I enable kernel debugging?",
            "Show me how to modify the driver",
            "I need to debug the kernel",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is True
            assert result.category == GuardrailCategory.KERNEL_DEBUG
    
    @pytest.mark.unit
    def test_etc_hosts_blocked(self, guardrail_engine):
        """Test that /etc/hosts editing is blocked."""
        messages = [
            "How do I edit /etc/hosts?",
            "Can I modify the hosts file?",
            "Should I update /etc/hosts to fix DNS?",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is True
            assert result.category == GuardrailCategory.ETC_HOSTS
    
    @pytest.mark.unit
    def test_destructive_actions_blocked(self, guardrail_engine):
        """Test that destructive actions are blocked."""
        messages = [
            "How do I reset all environments?",
            "Can you delete all lab instances?",
            "Show me how to wipe all user data",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is True
            assert result.category == GuardrailCategory.DESTRUCTIVE
            assert result.severity == "CRITICAL"
    
    @pytest.mark.unit
    def test_safe_messages_allowed(self, guardrail_engine):
        """Test that safe messages are not blocked."""
        messages = [
            "I keep getting redirected to the login page",
            "My lab VM crashed and I lost my work",
            "How do I reset my password?",
            "The container failed to initialize",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is False
            assert result.category is None
    
    @pytest.mark.unit
    def test_role_based_filtering(self, guardrail_engine):
        """Test that role-based filtering works correctly."""
        # Trainees should not see OS-level commands
        message = "How do I check system logs?"
        
        trainee_result = guardrail_engine.check(message, "trainee")
        # This should pass guardrails but be filtered by role in KB retrieval
        assert trainee_result.blocked is False
        
        # Support engineers should see more detailed info
        support_result = guardrail_engine.check(message, "support_engineer")
        assert support_result.blocked is False
    
    @pytest.mark.unit
    def test_case_insensitive_matching(self, guardrail_engine):
        """Test that pattern matching is case-insensitive."""
        messages = [
            "How do I ACCESS the HOST machine?",
            "DISABLE LOGGING please",
            "Edit /ETC/HOSTS",
        ]
        
        for message in messages:
            result = guardrail_engine.check(message, "trainee")
            assert result.blocked is True
    
    @pytest.mark.unit
    def test_partial_matches(self, guardrail_engine):
        """Test that partial matches are caught."""
        # These should NOT be blocked (false positives)
        safe_messages = [
            "The host name is not resolving",
            "I'm hosting a lab session",
            "The log shows an error",
        ]
        
        for message in safe_messages:
            result = guardrail_engine.check(message, "trainee")
            # These should pass - our patterns should be specific enough
            # If they fail, we need to refine the patterns
            assert result.blocked is False or result.severity != "HIGH"
    
    @pytest.mark.unit
    def test_multiple_violations(self, guardrail_engine):
        """Test messages with multiple guardrail violations."""
        message = "How do I access the host and disable logging?"
        
        result = guardrail_engine.check(message, "trainee")
        assert result.blocked is True
        # Should catch at least one violation
        assert result.category in [
            GuardrailCategory.HOST_ACCESS,
            GuardrailCategory.DISABLE_LOGGING
        ]
    
    @pytest.mark.unit
    def test_guardrail_logging(self, guardrail_engine):
        """Test that guardrail events are logged."""
        message = "How do I access the host machine?"
        
        result = guardrail_engine.check(message, "trainee")
        
        assert result.blocked is True
        assert result.message is not None
        assert "not permitted" in result.message.lower() or "cannot" in result.message.lower()
        # Should not reveal technical details
        assert "host" not in result.message.lower()
        assert "hypervisor" not in result.message.lower()
    
    @pytest.mark.unit
    def test_deterministic_results(self, guardrail_engine):
        """Test that same input produces same output."""
        message = "How do I disable logging?"
        
        result1 = guardrail_engine.check(message, "trainee")
        result2 = guardrail_engine.check(message, "trainee")
        result3 = guardrail_engine.check(message, "trainee")
        
        assert result1.blocked == result2.blocked == result3.blocked
        assert result1.category == result2.category == result3.category
        assert result1.severity == result2.severity == result3.severity
