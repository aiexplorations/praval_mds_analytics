# Testing Quick Start
**Get up and running with tests in 5 minutes**

---

## 1. Install Test Dependencies (One-time setup)

```bash
# Ensure virtual environment exists
python3 -m venv venv

# Install all dependencies including test tools
./venv/bin/pip install -r requirements.txt
```

---

## 2. Run Tests

```bash
# Run all tests
make test

# Or run specific test suites
make test-unit          # Fast, isolated tests
make test-integration   # Tests with databases
make test-e2e           # Full system tests
```

---

## 3. Deploy with Test-First Workflow

```bash
# This runs all tests first, then starts containers
make deploy
```

**What happens:**
1. ✅ Runs unit tests
2. ✅ Runs integration tests
3. ✅ Checks coverage (target: 80%)
4. ✅ Runs dbt tests
5. 🚀 Starts Docker containers (only if tests pass)
6. ✅ Runs E2E smoke tests
7. 🎉 Shows access URLs

---

## 4. Check Coverage

```bash
make coverage
# Opens: htmlcov/index.html
```

---

## Common Commands

```bash
# Development workflow
make test              # Run all tests
make deploy            # Test + deploy containers
make clean             # Clean cache files

# Container management
make start             # Start containers (skip tests)
make stop              # Stop containers
make restart           # Restart containers
make logs              # View container logs

# Help
make help              # Show all commands
```

---

## Current Test Status

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| EL Pipeline | 6 | 70% | ✅ Good |
| Agents | 13 | 15% | ⚠️ Needs work |
| dbt | Schema only | 20% | ⚠️ Needs work |
| Cube.js | 0 | 0% | ❌ None |
| Frontend | 0 | 0% | ❌ None |
| **Overall** | **19** | **25%** | ⚠️ |

**Target:** 203+ tests, 90% coverage (95%+ for critical modules)

---

## Writing Your First Test

```python
# tests/unit/test_example.py
import pytest

@pytest.mark.unit
def test_example():
    """Test that addition works."""
    result = 2 + 2
    assert result == 4
```

Run it:
```bash
pytest tests/unit/test_example.py -v
```

---

## Next Steps

1. ✅ **You are here:** Basic setup and running tests
2. 📖 Read `docs/TESTING_GUIDE.md` for detailed information
3. 🔧 Review `docs/testing_enhancement.md` for the full test plan
4. 💻 Start implementing missing tests (see Phase 1 in testing_enhancement.md)

---

## Need Help?

- Run: `make help`
- View test plan: `docs/testing_enhancement.md`
- Full guide: `docs/TESTING_GUIDE.md`
- pytest help: `pytest --help`
