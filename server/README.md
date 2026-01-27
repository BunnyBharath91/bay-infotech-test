# AI Help Desk Backend

Enterprise-grade AI Help Desk system with RAG pipeline, deterministic business logic, and comprehensive safety guardrails.

## Features

- **KB-Grounded RAG**: Retrieval-Augmented Generation using only local Knowledge Base
- **Deterministic Classification**: Rule-based tier, severity, and escalation logic
- **Safety Guardrails**: Pattern-based content filtering and role-based access control
- **Provider-Agnostic LLM**: Support for OpenAI, Anthropic, Vertex AI, or mock providers
- **Vector Search**: PostgreSQL + pgvector for semantic search
- **Analytics**: Real-time metrics and deflection rate tracking

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension (or use Neon)
- LLM API key (OpenAI, Anthropic, or Vertex AI)

### Local Development

1. **Clone and setup:**

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database:**

```bash
python scripts/init_db.py
python scripts/ingest_kb.py
```

4. **Run server:**

```bash
uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

### Docker Development

```bash
docker-compose up
```

## API Endpoints

### Chat
- `POST /api/chat` - Process chat message

### Tickets
- `GET /api/tickets` - List tickets
- `GET /api/tickets/{id}` - Get ticket details
- `GET /api/tickets/session/{session_id}` - Get session tickets

### Metrics
- `GET /api/metrics/summary` - Get metrics summary
- `GET /api/metrics/trends` - Get trend data

## Configuration

Key environment variables:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
LLM_PROVIDER=openai  # openai, anthropic, vertex, mock
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-4
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Architecture

```
server/
├── app/
│   ├── api/          # FastAPI routes
│   ├── core/         # Business logic (guardrails, tiering, escalation)
│   ├── rag/          # RAG pipeline (ingestion, retrieval, ranking)
│   ├── llm/          # LLM provider abstraction
│   ├── db/           # Database models and repositories
│   └── schemas/      # Pydantic schemas
├── kb/               # Knowledge Base markdown files
├── scripts/          # Database initialization scripts
└── tests/            # Test suite
```

## Testing

```bash
pytest
```

## Deployment

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed deployment instructions.

## License

Proprietary - BayInfotech
