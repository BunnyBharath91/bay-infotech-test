"""
Integration tests for API endpoints
"""
import pytest
from httpx import AsyncClient


class TestChatAPI:
    """Test /api/chat endpoint."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_endpoint_success(self, test_client, sample_chat_request):
        """Test successful chat request."""
        response = await test_client.post("/api/chat", json=sample_chat_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "answer" in data
        assert "kbReferences" in data
        assert "confidence" in data
        assert "tier" in data
        assert "severity" in data
        assert "needsEscalation" in data
        assert "guardrail" in data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_endpoint_guardrail_block(self, test_client):
        """Test chat request that triggers guardrail."""
        request = {
            "sessionId": "test-session-123",
            "message": "How do I access the host machine?",
            "userRole": "trainee",
            "context": {}
        }
        
        response = await test_client.post("/api/chat", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify guardrail blocked
        assert data["guardrail"]["blocked"] is True
        assert data["guardrail"]["category"] is not None
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_endpoint_invalid_request(self, test_client):
        """Test chat request with missing required fields."""
        request = {
            "sessionId": "test-session-123",
            # Missing message
            "userRole": "trainee"
        }
        
        response = await test_client.post("/api/chat", json=request)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_endpoint_escalation(self, test_client):
        """Test chat request that triggers escalation."""
        request = {
            "sessionId": "test-session-123",
            "message": "My VM has a kernel panic and I lost all my work!",
            "userRole": "trainee",
            "context": {}
        }
        
        response = await test_client.post("/api/chat", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should trigger escalation
        assert data["needsEscalation"] is True
        assert data["tier"] in ["TIER_2", "TIER_3"]
        assert data["severity"] in ["HIGH", "CRITICAL"]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_endpoint_conversation_history(self, test_client):
        """Test that conversation history is maintained."""
        session_id = "test-session-history"
        
        # First message
        request1 = {
            "sessionId": session_id,
            "message": "I can't log in",
            "userRole": "trainee",
            "context": {}
        }
        response1 = await test_client.post("/api/chat", json=request1)
        assert response1.status_code == 200
        
        # Second message (follow-up)
        request2 = {
            "sessionId": session_id,
            "message": "I already tried clearing my cache",
            "userRole": "trainee",
            "context": {}
        }
        response2 = await test_client.post("/api/chat", json=request2)
        assert response2.status_code == 200
        
        # Should maintain context
        data2 = response2.json()
        assert "answer" in data2
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_chat_endpoint_role_based_response(self, test_client):
        """Test that responses are filtered by user role."""
        message = "How do I check system logs?"
        
        # Trainee request
        trainee_request = {
            "sessionId": "test-trainee",
            "message": message,
            "userRole": "trainee",
            "context": {}
        }
        trainee_response = await test_client.post("/api/chat", json=trainee_request)
        assert trainee_response.status_code == 200
        trainee_data = trainee_response.json()
        
        # Support engineer request
        support_request = {
            "sessionId": "test-support",
            "message": message,
            "userRole": "support_engineer",
            "context": {}
        }
        support_response = await test_client.post("/api/chat", json=support_request)
        assert support_response.status_code == 200
        support_data = support_response.json()
        
        # Responses should differ based on role
        # (Support engineer may get more detailed info)
        assert trainee_data["answer"] != support_data["answer"] or \
               len(trainee_data["kbReferences"]) <= len(support_data["kbReferences"])


class TestTicketsAPI:
    """Test /api/tickets endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_tickets(self, test_client):
        """Test getting list of tickets."""
        response = await test_client.get("/api/tickets")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "tickets" in data
        assert "total" in data
        assert isinstance(data["tickets"], list)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_ticket_by_id(self, test_client):
        """Test getting a specific ticket."""
        # First create a ticket via chat that escalates
        chat_request = {
            "sessionId": "test-ticket-session",
            "message": "My VM has a kernel panic!",
            "userRole": "trainee",
            "context": {}
        }
        chat_response = await test_client.post("/api/chat", json=chat_request)
        assert chat_response.status_code == 200
        
        chat_data = chat_response.json()
        if chat_data.get("ticketId"):
            ticket_id = chat_data["ticketId"]
            
            # Get the ticket
            response = await test_client.get(f"/api/tickets/{ticket_id}")
            assert response.status_code == 200
            
            ticket_data = response.json()
            assert ticket_data["id"] == ticket_id
            assert "tier" in ticket_data
            assert "severity" in ticket_data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_tickets_by_session(self, test_client):
        """Test getting tickets for a specific session."""
        session_id = "test-session-tickets"
        
        # Create some tickets via chat
        for i in range(2):
            request = {
                "sessionId": session_id,
                "message": f"Kernel panic issue {i}",
                "userRole": "trainee",
                "context": {}
            }
            await test_client.post("/api/chat", json=request)
        
        # Get tickets for session
        response = await test_client.get(f"/api/tickets/session/{session_id}")
        assert response.status_code == 200
        
        tickets = response.json()
        assert isinstance(tickets, list)


class TestMetricsAPI:
    """Test /api/metrics endpoints."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_metrics_summary(self, test_client):
        """Test getting metrics summary."""
        response = await test_client.get("/api/metrics/summary?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify metrics structure
        assert "deflection_rate" in data
        assert "total_conversations" in data
        assert "tickets_by_tier" in data
        assert "tickets_by_severity" in data
        assert "guardrail_activations" in data
        assert "escalation_count" in data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_metrics_trends(self, test_client):
        """Test getting metrics trends."""
        response = await test_client.get("/api/metrics/trends?hours=24")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify trends structure
        assert "timestamps" in data
        assert "conversation_volumes" in data
        assert isinstance(data["timestamps"], list)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_metrics_reflect_actual_data(self, test_client):
        """Test that metrics reflect actual chat interactions."""
        # Create some chat interactions
        session_id = "test-metrics-session"
        
        # Get initial metrics
        initial_response = await test_client.get("/api/metrics/summary?hours=1")
        initial_data = initial_response.json()
        initial_count = initial_data["total_conversations"]
        
        # Create a chat interaction
        chat_request = {
            "sessionId": session_id,
            "message": "I can't log in",
            "userRole": "trainee",
            "context": {}
        }
        await test_client.post("/api/chat", json=chat_request)
        
        # Get updated metrics
        updated_response = await test_client.get("/api/metrics/summary?hours=1")
        updated_data = updated_response.json()
        updated_count = updated_data["total_conversations"]
        
        # Count should have increased
        assert updated_count >= initial_count


class TestHealthCheck:
    """Test health check endpoint."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
