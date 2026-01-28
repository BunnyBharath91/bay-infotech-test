# AI Help Desk Backend

Enterprise-grade AI Help Desk system with RAG pipeline, deterministic business logic, and comprehensive safety guardrails.

## Features

- **KB-Grounded RAG**: Retrieval-Augmented Generation using only local Knowledge Base
- **Deterministic Classification**: Rule-based tier, severity, and escalation logic
- **Safety Guardrails**: Pattern-based content filtering and role-based access control
- **Provider-Agnostic LLM**: Support for OpenAI, Anthropic, Gemini, or mock providers
- **SQLite for Local Dev**: Simple file-based DB (`helpdesk.db`) with pure-Python vector similarity
- **PostgreSQL + pgvector in Production**: True vector similarity search for large-scale deployments
- **Analytics**: Real-time metrics and deflection rate tracking

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for running the full stack)
- **Local development database:** SQLite (no separate DB install needed)
- **Production database:** PostgreSQL 15+ with pgvector extension (Neon/Render/etc.)
- Optional: LLM API key (OpenAI, Anthropic, Gemini) if you want live LLM responses

### Local Development (SQLite)

This is the recommended flow for contributors so you don’t need a local PostgreSQL.

1. **Create and activate virtualenv (Python 3.11):**

   ```bash
   cd server

   # On Windows (recommended):
   py -3.11 -m venv venv
   # On macOS / Linux:
   # python3.11 -m venv venv

   # Activate
   source venv/bin/activate        # On Windows: venv\Scripts\activate

   pip install -r requirements.txt
   ```

2. **Configure environment (SQLite by default):**

   ```bash
   cp .env.example .env
   ```

   Key points for local dev:
   - `DATABASE_URL=sqlite+aiosqlite:///./helpdesk.db` (no Postgres required)
   - You can run in **KB-only mode** (no external LLM) by setting in `.env`:

     ```env
     USE_LLM=false
     LLM_PROVIDER=mock
     ```

3. **Initialize SQLite database and ingest KB:**

   ```bash
   # From server/ with venv activated
   python full_reset.py      # drops/recreates all tables in helpdesk.db
   python simple_ingest.py   # parses server/kb and stores chunks + embeddings
   ```

4. **Run server on port 8000:**

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

   The backend will be available at:
   - `http://localhost:8000`
   - Docs: `http://localhost:8000/docs`

### Production / PostgreSQL + pgvector

For production (Render, Neon, etc.) use PostgreSQL with pgvector and the deployment scripts:

1. Set in `.env` (or platform env vars):

   ```env
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
   ```

2. Initialize schema and ingest KB using the scripts:

   ```bash
   python scripts/init_db.py
   python scripts/ingest_kb.py
   ```

3. Run the server behind your chosen process manager / container runtime.

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
