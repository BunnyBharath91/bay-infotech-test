# API Documentation

Base URL: `https://your-backend.onrender.com` (production) or `http://localhost:8000` (development)

## Authentication

Currently no authentication required. In production, implement JWT or API key authentication.

## Endpoints

### Chat API

#### POST /api/chat

Process a chat message and return AI-generated response.

**Request Body:**

```json
{
  "sessionId": "uuid-123",
  "message": "I keep getting redirected to the login page after I log in.",
  "userRole": "trainee",
  "context": {
    "module": "lab-7",
    "channel": "self-service-portal"
  }
}
```

**Response:**

```json
{
  "answer": "Based on kb-access-authentication, here are the steps to resolve the login redirection issue...",
  "kbReferences": [
    {
      "id": "kb-access-authentication",
      "title": "Access and Authentication Troubleshooting",
      "version": "2.1",
      "relevance_score": 0.95
    }
  ],
  "confidence": 0.93,
  "tier": "TIER_0",
  "severity": "MEDIUM",
  "needsEscalation": false,
  "guardrail": {
    "blocked": false,
    "reason": null,
    "trigger_type": null
  },
  "ticketId": null,
  "sessionId": "uuid-123"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request
- 500: Server error

---

### Tickets API

#### GET /api/tickets

List all tickets with pagination.

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20, max: 100): Items per page

**Response:**

```json
{
  "tickets": [
    {
      "id": "INC-A1B2C3D4",
      "session_id": "uuid-123",
      "tier": "TIER_2",
      "severity": "HIGH",
      "subject": "Lab VM crash with lost progress",
      "description": "Issue: My lab VM froze...",
      "status": "New",
      "created_at": "2024-06-01T10:30:00Z",
      "updated_at": "2024-06-01T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

#### GET /api/tickets/{ticket_id}

Get specific ticket details.

**Response:**

```json
{
  "id": "INC-A1B2C3D4",
  "session_id": "uuid-123",
  "tier": "TIER_2",
  "severity": "HIGH",
  "subject": "Lab VM crash",
  "description": "Full description...",
  "status": "New",
  "created_at": "2024-06-01T10:30:00Z",
  "updated_at": "2024-06-01T10:30:00Z"
}
```

#### GET /api/tickets/session/{session_id}

Get all tickets for a specific session.

**Response:**

```json
[
  {
    "id": "INC-A1B2C3D4",
    "session_id": "uuid-123",
    ...
  }
]
```

---

### Metrics API

#### GET /api/metrics/summary

Get summary metrics for specified time period.

**Query Parameters:**
- `hours` (integer, default: 24, max: 168): Hours to look back

**Response:**

```json
{
  "deflection_rate": 65.5,
  "total_conversations": 1250,
  "total_tickets": 432,
  "tickets_by_tier": {
    "TIER_0": 818,
    "TIER_1": 215,
    "TIER_2": 180,
    "TIER_3": 37
  },
  "tickets_by_severity": {
    "LOW": 520,
    "MEDIUM": 380,
    "HIGH": 310,
    "CRITICAL": 40
  },
  "guardrail_activations": {
    "total_activations": 45,
    "blocked_requests": 38,
    "by_type": {
      "host_access": 15,
      "disable_logging": 12,
      "etc_hosts": 8,
      "destructive": 3
    }
  },
  "escalation_count": 215,
  "time_period": "Last 24 hours"
}
```

#### GET /api/metrics/trends

Get trend data over time (implementation pending).

---

## Data Models

### UserRole Enum
- `trainee`
- `instructor`
- `operator`
- `support_engineer`
- `admin`

### Tier Enum
- `TIER_0`: Self-service via KB
- `TIER_1`: Human generalist
- `TIER_2`: Support Engineer
- `TIER_3`: Platform Engineering

### Severity Enum
- `LOW`: Minor inconvenience
- `MEDIUM`: User blocked
- `HIGH`: Multiple users blocked
- `CRITICAL`: System-wide outage or data loss

### TicketStatus Enum
- `New`
- `In Progress`
- `Resolved`
- `Closed`

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Error Codes:**
- 400: Bad Request (invalid input)
- 404: Not Found (resource doesn't exist)
- 422: Validation Error (Pydantic validation failed)
- 500: Internal Server Error

---

## Rate Limiting

Currently no rate limiting implemented. Recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per session

---

## CORS

Configured origins (can be updated in backend config):
- `http://localhost:5173` (Vite dev)
- `http://localhost:3000` (React dev)
- Production frontend URL

---

## Health Check

#### GET /health

Simple health check endpoint.

**Response:**

```json
{
  "status": "healthy"
}
```

#### GET /

Root endpoint with API information.

**Response:**

```json
{
  "name": "AI Help Desk",
  "version": "1.0.0",
  "status": "operational"
}
```
