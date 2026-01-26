# Test Suite Documentation

Comprehensive test suite for the AI Help Desk backend.

## Overview

The test suite includes:
- **Unit Tests**: Core business logic (guardrails, tiering, escalation, severity, RAG)
- **Integration Tests**: API endpoints (chat, tickets, metrics)
- **E2E Tests**: All 12 required workflows
- **Coverage Target**: >80% overall, >95% for core logic

## Running Tests

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E workflow tests only
pytest -m e2e

# Specific workflow tests
pytest -m workflow
```

### Run Specific Test Files

```bash
# Guardrails tests
pytest tests/test_guardrails.py

# Tiering tests
pytest tests/test_tiering.py

# All workflow tests
pytest tests/test_workflows.py

# Specific workflow
pytest tests/test_workflows.py::TestWorkflow01
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Run with Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_guardrails.py       # Guardrail engine tests
├── test_tiering.py          # Tier classification tests
├── test_severity.py         # Severity classification tests
├── test_escalation.py       # Escalation logic tests
├── test_rag.py              # RAG pipeline tests
├── test_api.py              # API endpoint tests
└── test_workflows.py        # E2E workflow tests
```

## Test Fixtures

### Database Fixtures

- `test_db_engine`: Creates in-memory SQLite database for tests
- `test_db_session`: Provides database session for tests
- `test_client`: HTTP client with database dependency override

### Sample Data Fixtures

- `sample_chat_request`: Standard chat request payload
- `sample_kb_chunks`: Sample KB chunks for testing
- `mock_llm_response`: Mock LLM response

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:

- **Guardrails** (`test_guardrails.py`):
  - Pattern matching for forbidden actions
  - Role-based filtering
  - Case-insensitive matching
  - Deterministic results

- **Tiering** (`test_tiering.py`):
  - TIER_0 to TIER_3 classification
  - Escalation on repeated failures
  - Deterministic classification

- **Severity** (`test_severity.py`):
  - LOW to CRITICAL classification
  - Priority ordering
  - Deterministic results

- **Escalation** (`test_escalation.py`):
  - Mandatory escalation triggers
  - User preference ignored
  - Deterministic decisions

- **RAG** (`test_rag.py`):
  - Embedding generation
  - Chunk retrieval
  - Conflict resolution
  - Role-based filtering

### Integration Tests (`@pytest.mark.integration`)

Test API endpoints with database:

- **Chat API** (`test_api.py`):
  - Successful requests
  - Guardrail blocking
  - Escalation triggers
  - Conversation history
  - Role-based responses

- **Tickets API** (`test_api.py`):
  - List tickets
  - Get ticket by ID
  - Get tickets by session

- **Metrics API** (`test_api.py`):
  - Summary metrics
  - Trends over time
  - Data accuracy

### E2E Tests (`@pytest.mark.e2e`, `@pytest.mark.workflow`)

Test complete workflows end-to-end:

1. **Authentication Loop Failure**: KB-grounded resolution
2. **Lab VM Crash**: Critical issue handling
3. **Incorrect Environment**: Environment mapping
4. **Container Init Failure**: Infrastructure issue
5. **Unauthorized Access**: Guardrail blocking
6. **Disable Logging**: Security guardrail
7. **Conflicting KB**: Conflict resolution
8. **Time Drift**: Edge case handling
9. **DNS Error**: No /etc/hosts editing
10. **Destructive Action**: Critical guardrail
11. **Kernel Panic**: Mandatory escalation
12. **Override Escalation**: User preference ignored

## Test Requirements

### Passing Criteria

All tests must pass with:
- ✅ No hallucinations (KB-grounded only)
- ✅ Correct tier/severity classification
- ✅ Guardrails block unsafe requests
- ✅ Escalation rules followed
- ✅ Deterministic results
- ✅ Analytics accuracy

### Coverage Requirements

- Overall: >80%
- Core logic (guardrails, tiering, escalation): >95%
- RAG pipeline: >85%
- API endpoints: >75%

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Every push to main
- Every pull request
- Nightly builds

### Pre-commit Hooks

Run tests before committing:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Debugging Tests

### Run Single Test

```bash
pytest tests/test_guardrails.py::TestGuardrailEngine::test_host_access_blocked -v
```

### Print Output

```bash
pytest -s  # Show print statements
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Show Locals on Failure

```bash
pytest -l
```

## Common Issues

### Database Connection Errors

Tests use in-memory SQLite by default. If you see connection errors:

```bash
# Check DATABASE_URL is not set in test environment
unset DATABASE_URL
pytest
```

### Import Errors

Make sure you're in the backend directory:

```bash
cd backend
pytest
```

### Async Test Errors

Ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

## Writing New Tests

### Test Template

```python
import pytest

class TestMyFeature:
    """Test my new feature."""
    
    @pytest.mark.unit
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        input_data = "test"
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result is not None
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_endpoint(self, test_client):
        """Test API endpoint."""
        response = await test_client.post("/api/test", json={})
        assert response.status_code == 200
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is tested
3. **Arrange-Act-Assert** pattern
4. **Use fixtures** for common setup
5. **Mark tests** appropriately (unit, integration, e2e)
6. **Test edge cases** and error conditions
7. **Keep tests fast** (use mocks for slow operations)

## Test Data

### Sample Messages

Located in `conftest.py`:
- Authentication issues
- Lab crashes
- Container failures
- Guardrail triggers

### KB Test Data

Sample KB chunks for testing retrieval and ranking.

## Performance

### Test Execution Time

- Unit tests: <10 seconds
- Integration tests: <30 seconds
- E2E tests: <60 seconds
- Full suite: <2 minutes

### Optimization

- Use in-memory database
- Parallel test execution: `pytest -n auto`
- Skip slow tests: `pytest -m "not slow"`

## Reporting

### HTML Report

```bash
pytest --html=report.html --self-contained-html
```

### JUnit XML (for CI)

```bash
pytest --junitxml=junit.xml
```

### Coverage Report

```bash
pytest --cov=app --cov-report=html
```

## Support

For test issues:
1. Check this README
2. Review test logs
3. Check CI/CD pipeline
4. Contact: [your-email@bayinfotech.com]
