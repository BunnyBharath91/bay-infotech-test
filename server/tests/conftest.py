"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.db.models import Base
from app.api.dependencies import get_db
from app.main import app
from app.config import get_settings

settings = get_settings()


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
async def test_client(test_db_session):
    """Create a test client with dependency overrides."""
    from httpx import AsyncClient, ASGITransport
    
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "sessionId": "test-session-123",
        "message": "I keep getting redirected to the login page after I log in.",
        "userRole": "trainee",
        "context": {
            "module": "lab-7",
            "channel": "self-service-portal"
        }
    }


@pytest.fixture
def sample_kb_chunks():
    """Sample KB chunks for testing."""
    return [
        {
            "id": "chunk-1",
            "kb_document_id": "01-access-and-authentication-v2.1",
            "chunk_text": "If you experience login redirection issues, clear your browser cache and cookies.",
            "heading_path": "Authentication > Login Issues",
            "version": "2.1",
            "last_updated": "2024-01-15"
        },
        {
            "id": "chunk-2",
            "kb_document_id": "01-access-and-authentication-v2.1",
            "chunk_text": "Check if your session has expired. Sessions expire after 30 minutes of inactivity.",
            "heading_path": "Authentication > Session Management",
            "version": "2.1",
            "last_updated": "2024-01-15"
        }
    ]


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return """Based on the knowledge base, here are the steps to resolve login redirection issues:

1. Clear your browser cache and cookies
2. Check if your session has expired (sessions expire after 30 minutes)
3. Try logging in again with a fresh browser session

This information is from KB document 01-access-and-authentication-v2.1."""
