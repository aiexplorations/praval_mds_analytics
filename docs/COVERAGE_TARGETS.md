# Code Coverage Targets
**90% Overall Coverage Strategy**

---

## Coverage Targets by Module

### Critical Modules (95%+ Required)

#### el_pipeline/ - **Target: 95%+**
**Rationale:** Data pipeline is mission-critical. Data loss or corruption would be catastrophic.

| File | Target | Priority |
|------|--------|----------|
| `config.py` | 95% | HIGH |
| `database.py` | 98% | CRITICAL |
| `extractor.py` | 95% | CRITICAL |
| `loader.py` | 98% | CRITICAL |
| `pipeline.py` | 95% | CRITICAL |
| `cli.py` | 90% | MEDIUM |

**Why 95%+:**
- Handles all data extraction and loading
- Database connection management
- Transaction handling
- Error recovery critical

#### agents/ - **Target: 92%+**
**Rationale:** Agents are the user-facing intelligence layer. Bugs directly impact UX.

| File | Target | Priority |
|------|--------|----------|
| `manufacturing_advisor.py` | 95% | CRITICAL |
| `analytics_specialist.py` | 95% | CRITICAL |
| `visualization_specialist.py` | 92% | HIGH |
| `quality_inspector.py` | 92% | HIGH |
| `report_writer.py` | 92% | HIGH |
| `cubejs_client.py` | 95% | CRITICAL |
| `session_manager.py` | 90% | HIGH |
| `app.py` | 88% | MEDIUM |
| `reef_config.py` | 90% | HIGH |
| `spore_schemas.py` | 85% | MEDIUM |
| `models.py` | 80% | LOW |
| `config.py` | 80% | LOW |

**Why 92%+:**
- Complex LLM interaction logic
- User experience depends on correctness
- Multi-agent coordination critical
- Session state management

---

### Business Logic (90%+ Required)

#### dbt_transform/ - **Target: 90%+**
**Rationale:** Business logic and calculations must be accurate.

| Component | Target | Priority |
|-----------|--------|----------|
| Staging models | 90% | HIGH |
| Intermediate models | 95% | CRITICAL |
| Mart models | 95% | CRITICAL |
| Custom tests | 100% | CRITICAL |
| Schema tests | 100% | CRITICAL |

**Why 90%+:**
- OEE calculations must be accurate
- Financial calculations (costs) must be correct
- Aggregations must match raw data
- Business rules must be validated

---

### Integration Layer (85%+ Required)

#### cubejs/ - **Target: 85%+**
**Rationale:** Semantic layer provides consistent metrics.

| Component | Target | Priority |
|-----------|--------|----------|
| Schema definitions | 90% | HIGH |
| Measure calculations | 95% | CRITICAL |
| Dimension logic | 85% | MEDIUM |
| Pre-aggregations | 80% | MEDIUM |

**Why 85%+:**
- Metric definitions must be tested
- Calculation accuracy verified
- Query generation validated

---

### Frontend (88%+ Required)

#### frontend/ - **Target: 88%+**
**Rationale:** User interface must work correctly across browsers.

| Component | Target | Priority |
|-----------|--------|----------|
| ChatInterface | 95% | CRITICAL |
| Chart components | 90% | HIGH |
| API client | 95% | CRITICAL |
| State management | 90% | HIGH |
| Utility functions | 85% | MEDIUM |
| UI components | 85% | MEDIUM |

**Why 88%+:**
- User interaction logic critical
- Chart rendering must work
- API calls must be resilient
- State consistency important

---

### Infrastructure (85%+ Required)

#### airflow/ - **Target: 85%+**
**Rationale:** Orchestration must be reliable.

| Component | Target | Priority |
|-----------|--------|----------|
| DAG definitions | 90% | HIGH |
| Task logic | 85% | HIGH |
| Error handling | 90% | HIGH |

**Why 85%+:**
- Scheduled jobs must execute correctly
- Error handling critical
- Dependencies must be right

---

## Coverage Strategy

### Phase 1: Critical Unit Tests (Week 1)
**Target: 70% overall**
- Focus on el_pipeline and agents unit tests
- Mock external dependencies
- Fast execution (<2 minutes)

**Module Targets:**
- el_pipeline: 85%
- agents: 60%
- dbt: 20% (schema only)
- cubejs: 0%
- frontend: 0%

### Phase 2: Integration Tests (Week 2)
**Target: 80% overall**
- Multi-agent integration
- Database integration
- Cube.js integration
- dbt business logic

**Module Targets:**
- el_pipeline: 90%
- agents: 75%
- dbt: 90%
- cubejs: 85%
- frontend: 0%

### Phase 3: Advanced Testing (Week 3)
**Target: 85% overall**
- Property-based testing
- Mutation testing
- Security scanning
- Infrastructure tests

**Module Targets:**
- el_pipeline: 95%
- agents: 85%
- dbt: 90%
- cubejs: 85%
- frontend: 50%

### Phase 4: Frontend & E2E (Week 4)
**Target: 90%+ overall**
- Frontend component tests
- E2E tests
- Performance tests
- Chaos engineering

**Module Targets:**
- el_pipeline: 95%+
- agents: 92%+
- dbt: 90%+
- cubejs: 85%+
- frontend: 88%+

---

## Coverage Enforcement

### Local Development
```bash
# Check coverage before commit
make coverage

# Coverage threshold enforced in pytest.ini
pytest --cov --cov-fail-under=90
```

### CI/CD Pipeline
```yaml
# GitHub Actions enforces coverage
- name: Check coverage
  run: |
    pytest --cov --cov-fail-under=90
    # Fails CI if below 90%
```

### Pre-Commit Hooks
```yaml
# Optional: Enforce coverage on commit
- id: pytest-check-coverage
  entry: pytest --cov --cov-fail-under=90
```

---

## Measuring Coverage

### Generate Reports
```bash
# HTML report (detailed)
pytest --cov --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov --cov-report=term-missing

# XML report (for CI)
pytest --cov --cov-report=xml
```

### By Module
```bash
# Specific module
pytest --cov=el_pipeline --cov-report=term-missing

# Multiple modules
pytest --cov=el_pipeline --cov=agents --cov-report=term-missing
```

### Coverage Gaps
```bash
# Show missing lines
pytest --cov --cov-report=term-missing

# Focus on gaps
pytest --cov --cov-report=term:skip-covered
```

---

## What 90% Means

### Lines Covered
- 90% of executable lines have tests
- Focus on business logic, not boilerplate
- Exclude: type definitions, simple getters, constants

### Branch Coverage
- 90% of conditional branches tested
- All if/else paths covered
- Exception paths tested

### Not Just Numbers
**Quality over quantity:**
- Tests must be meaningful
- Edge cases must be covered
- Error conditions tested
- Integration points validated

**What we DON'T count toward 90%:**
- Type definition files
- Auto-generated code
- Simple property getters
- Configuration constants
- Third-party packages

---

## Maintaining 90%

### For New Code
- Write tests first (TDD)
- Aim for 95%+ on new modules
- Don't merge if coverage drops

### For Bug Fixes
- Add test that reproduces bug
- Fix bug
- Verify test passes
- Check coverage didn't drop

### For Refactoring
- Maintain or improve coverage
- Don't delete tests
- Update tests if needed

---

## When to Allow <90%

### Acceptable Exceptions
1. **Legacy code being deprecated**
   - Document exception
   - Plan removal date

2. **External API wrappers**
   - Mock tests sufficient
   - Integration tests cover real usage

3. **Configuration/Constants**
   - No logic to test
   - Validated indirectly

4. **Generated code**
   - dbt packages
   - Protobuf definitions

### Process for Exceptions
```python
# Add pragma to exclude from coverage
def deprecated_function():  # pragma: no cover
    """This function is deprecated."""
    pass
```

Update `.coveragerc`:
```ini
[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

---

## Coverage Anti-Patterns

### ❌ Don't Do This

**Bad Test (Just for coverage):**
```python
def test_function_runs():
    """Test that function doesn't crash."""
    function()  # No assertions!
```

**Mock Everything:**
```python
def test_with_all_mocks(mock1, mock2, mock3, mock4):
    """Test with everything mocked."""
    # Testing mocks, not real code
```

**Testing Implementation Details:**
```python
def test_internal_variable_value():
    """Test internal implementation."""
    obj = MyClass()
    assert obj._internal_var == 5  # Fragile!
```

### ✅ Do This Instead

**Good Test (Meaningful):**
```python
def test_calculate_oee_correct():
    """Test OEE calculation is mathematically correct."""
    result = calculate_oee(
        availability=0.9,
        performance=0.95,
        quality=0.98
    )
    expected = 0.9 * 0.95 * 0.98
    assert abs(result - expected) < 0.001
```

**Strategic Mocking:**
```python
def test_with_external_mocked(mock_openai):
    """Test with external dependencies mocked."""
    # Mock only external dependencies
    # Test real business logic
```

**Testing Behavior:**
```python
def test_error_handling():
    """Test system handles errors gracefully."""
    with pytest.raises(ValueError, match="Invalid input"):
        process_data(invalid_input)
```

---

## Monitoring Coverage

### Weekly
- Run coverage report
- Check for drops
- Review untested code

### Per PR
- Coverage must not decrease
- New code must be >=95% covered
- CI fails if <90%

### Per Release
- Coverage report in release notes
- Track coverage trend
- Celebrate improvements!

---

## Tools

### Coverage Measurement
- **coverage.py** - Python coverage
- **pytest-cov** - pytest integration
- **Codecov** - Coverage tracking service

### Coverage Visualization
- **HTML reports** - Line-by-line
- **Codecov dashboard** - Trends
- **GitHub PR comments** - Per-PR changes

### Quality Tools
- **mutmut** - Mutation testing
- **hypothesis** - Property-based testing
- **bandit** - Security coverage

---

## Summary

**Target: 90%+ overall, 95%+ critical modules**

| Priority | Modules | Target | Rationale |
|----------|---------|--------|-----------|
| CRITICAL | el_pipeline, agents core | 95%+ | Data integrity, UX |
| HIGH | dbt, cubejs, frontend | 88-90% | Business logic, UI |
| MEDIUM | Infrastructure, config | 85%+ | Reliability |

**Remember:**
- Quality > Quantity
- Test behavior, not implementation
- Cover edge cases and errors
- Maintain coverage over time
- Celebrate hitting 90%! 🎉

---

**Path to 90%:**
Week 1 (70%) → Week 2 (80%) → Week 3 (85%) → Week 4 (90%+)
