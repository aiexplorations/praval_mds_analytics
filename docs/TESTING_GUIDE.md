# Testing Guide
## Praval Manufacturing Analytics System

This guide explains how to run tests and use the test-first deployment workflow.

---

## Quick Start

### Prerequisites
- Python 3.11+ with virtual environment set up
- Docker and Docker Compose
- All dependencies installed: `./venv/bin/pip install -r requirements.txt`

### Run All Tests
```bash
make test
```

### Deploy with Test-First Workflow
```bash
make deploy
```
This will:
1. Run all unit tests
2. Run all integration tests
3. Check coverage threshold
4. Run dbt tests
5. Start Docker containers (only if tests pass)
6. Run E2E smoke tests
7. Display access points

---

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests with no external dependencies.

**Run:**
```bash
make test-unit
# or
./venv/bin/pytest tests/unit -v
```

**Examples:**
- `test_config.py` - Configuration validation
- `test_manufacturing_advisor.py` - Agent logic (mocked)
- `test_cubejs_client.py` - API client (mocked)

### Integration Tests (`tests/integration/`)
Tests that interact with databases, external services, or multiple components.

**Run:**
```bash
make test-integration
# or
./venv/bin/pytest tests/integration -v
```

**Examples:**
- `test_database.py` - Real database connections
- `test_agent_collaboration.py` - Multi-agent flows
- `test_cubejs_schemas.py` - Cube.js queries

### End-to-End Tests (`tests/e2e/`)
Full system tests that verify entire workflows.

**Run:**
```bash
make test-e2e
# or
./venv/bin/pytest tests/e2e -v
```

**Examples:**
- `test_basic_smoke.py` - Basic functionality checks
- `test_full_data_pipeline.py` - Complete data flow

---

## Test Commands

### Basic Commands
```bash
# Run all tests
make test

# Run specific test suite
make test-unit
make test-integration
make test-e2e

# Generate coverage report
make coverage
# Opens: htmlcov/index.html
```

### Advanced Commands
```bash
# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m slow

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest tests/unit/agents/test_manufacturing_advisor.py -v

# Run specific test function
pytest tests/unit/agents/test_manufacturing_advisor.py::test_enrich_query_success -v

# Run with verbose output
pytest tests/unit -vv

# Stop on first failure
pytest tests/unit -x

# Run last failed tests
pytest --lf

# Show print statements
pytest -s
```

---

## Development Workflow

### Standard Workflow (Test-First)
```bash
# 1. Make code changes
vim agents/manufacturing_advisor.py

# 2. Run tests
make test

# 3. If tests pass, deploy
make deploy
```

### Quick Development Iteration
```bash
# Watch mode - auto-run tests on file change
pip install pytest-watch
ptw tests/unit -- -v
```

### Manual Deployment (without test check)
```bash
# Start containers directly (not recommended)
make start
# or
docker-compose up -d
```

---

## Writing Tests

### Test Structure
```python
"""Module description."""
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.unit
def test_function_scenario_expected_outcome():
    """Test that function does X when Y happens."""
    # Arrange
    mock_data = {"key": "value"}

    # Act
    result = function_under_test(mock_data)

    # Assert
    assert result == expected_value
```

### Using Fixtures
```python
# In conftest.py
@pytest.fixture
def sample_press_data():
    """Provide sample press operation data."""
    return {
        "part_family": "Door_Outer_Left",
        "oee": 0.85,
        "pass_rate": 0.95
    }

# In test file
def test_with_fixture(sample_press_data):
    """Test using fixture data."""
    assert sample_press_data["oee"] > 0.8
```

### Mocking External Services
```python
@pytest.mark.unit
@patch('agents.cubejs_client.httpx.AsyncClient')
async def test_cubejs_query(mock_client):
    """Test Cube.js query execution."""
    # Configure mock
    mock_client.return_value.post.return_value.json.return_value = {
        "data": [{"measure": 100}]
    }

    # Test
    result = await cubejs_client.execute_query(query)

    # Verify
    assert result["data"][0]["measure"] == 100
```

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test asynchronous agent function."""
    result = await agent.enrich_query("test query", [], "session-1")
    assert result["is_in_scope"] is True
```

---

## Coverage Requirements

### Coverage Thresholds
- **Overall:** 90% minimum
- **Critical modules:** 95%+ (agents, el_pipeline)
- **Business logic:** 90%+ (dbt models, Cube.js)
- **Frontend:** 88%+ (components, integration)
- **Infrastructure:** 85%+ (Airflow, Docker)

### Viewing Coverage
```bash
# Generate HTML report
make coverage

# Open in browser
open htmlcov/index.html

# Or view in terminal
pytest tests/ --cov --cov-report=term-missing
```

### Coverage by Module
```bash
# Specific module coverage
pytest tests/ --cov=el_pipeline --cov-report=term-missing
pytest tests/ --cov=agents --cov-report=term-missing
```

---

## CI/CD Integration

### Pre-Commit Hooks
Tests run automatically before each commit:
```bash
# Install hooks
pip install pre-commit
pre-commit install

# Now unit tests run on every commit
git commit -m "Add feature"
# → Runs pytest tests/unit
```

### GitHub Actions
Tests run automatically on push/PR:
- Unit tests → Integration tests → dbt tests → Build → E2E → Deploy

**View results:** GitHub Actions tab in repository

---

## Troubleshooting

### Tests Failing Locally

**Issue: Import errors**
```bash
# Solution: Ensure virtual environment is activated
source ./venv/bin/activate
pip install -r requirements.txt
```

**Issue: Database connection errors**
```bash
# Solution: Check Docker containers are running
docker-compose ps

# Restart if needed
docker-compose restart
```

**Issue: Port conflicts**
```bash
# Solution: Check what's using the port
lsof -i :5432

# Stop conflicting service or change port in docker-compose.yml
```

### Slow Test Execution

**Run tests in parallel:**
```bash
pip install pytest-xdist
pytest -n auto
```

**Skip slow tests:**
```bash
pytest -m "not slow"
```

### Mock Issues

**Issue: Mock not being called**
```python
# Check if you're patching the right location
# ❌ Wrong
@patch('openai.AsyncOpenAI')

# ✓ Correct (patch where it's imported)
@patch('agents.manufacturing_advisor.AsyncOpenAI')
```

---

## Test Data Management

### Test Fixtures Location
- `tests/conftest.py` - Shared fixtures
- `tests/fixtures/` - Test data factories
- `tests/fixtures/data/` - Static test data files

### Creating Test Data
```python
# Use factories for dynamic data
from tests.fixtures.factories import PressOperationFactory

press_op = PressOperationFactory.create(part_family="Door_Outer_Left")

# Or use static fixtures
@pytest.fixture
def sample_oee_data():
    return {
        "availability": 0.90,
        "performance": 0.95,
        "quality_rate": 0.98
    }
```

---

## Best Practices

### DO
- ✅ Write tests before fixing bugs
- ✅ Keep tests simple and focused
- ✅ Use descriptive test names
- ✅ Mock external dependencies
- ✅ Test edge cases and error conditions
- ✅ Run tests before committing
- ✅ Maintain test coverage above 80%

### DON'T
- ❌ Skip tests to save time
- ❌ Test implementation details
- ❌ Write flaky tests
- ❌ Commit broken tests
- ❌ Mock everything (integration tests need real components)
- ❌ Deploy without running tests

---

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.unit        # Fast, isolated
@pytest.mark.integration # Requires external services
@pytest.mark.e2e         # Full system test
@pytest.mark.slow        # Takes >5 seconds
```

Run specific markers:
```bash
pytest -m unit           # Only unit tests
pytest -m "not slow"     # Skip slow tests
pytest -m "integration or e2e"  # Integration or E2E
```

---

## Debugging Tests

### Use pytest debugging
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show local variables on failure
pytest -l
```

### Use print debugging
```bash
# Show print statements
pytest -s

# Verbose output
pytest -vv
```

### Use logging
```python
import logging
logger = logging.getLogger(__name__)

def test_something():
    logger.info("Debug info: %s", data)
    # Test code...
```

Run with logging:
```bash
pytest --log-cli-level=DEBUG
```

---

## Resources

- **pytest documentation:** https://docs.pytest.org/
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **unittest.mock:** https://docs.python.org/3/library/unittest.mock.html
- **Coverage.py:** https://coverage.readthedocs.io/

---

## Getting Help

**Common Commands:**
```bash
make help              # Show all make targets
pytest --help          # Show pytest options
pytest --markers       # Show available markers
pytest --fixtures      # Show available fixtures
```

**Questions?**
- Check `docs/testing_enhancement.md` for detailed test plan
- Review existing tests in `tests/` for examples
- Ask the team in #testing channel
