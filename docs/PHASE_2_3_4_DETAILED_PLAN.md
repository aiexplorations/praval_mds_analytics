# Phases 2-4: Detailed Implementation Plan
**Enhanced Testing Roadmap for 90% Coverage Target**

---

## Overview

This document provides the detailed implementation plan for Phases 2-4 of the testing enhancement roadmap. Phase 1 (Critical Unit Tests) is covered in the main testing_enhancement.md document.

**Updated Targets:**
- **Overall Coverage:** 90%+
- **Critical Modules (EL Pipeline, Agents):** 95%+
- **Total Tests:** 203+ (vs original 114+)
- **Enhanced Quality:** Property-based + mutation testing

---

## Phase 2: Integration Tests (Week 2, Days 8-14)

### Objectives
- Test multi-agent collaboration and communication
- Validate dbt business logic calculations
- Test Cube.js schema queries end-to-end
- Verify CLI and Airflow DAG functionality
- **Target: 80% coverage**

---

### Day 8-9: Multi-Agent Integration (Enhanced)

#### test_agent_collaboration.py (12 tests - enhanced from 8)

**Location:** `tests/integration/agents/test_agent_collaboration.py`

**New Tests:**

```python
"""Integration tests for multi-agent collaboration."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from praval import get_reef
from agents import (
    manufacturing_advisor,
    analytics_specialist,
    visualization_specialist,
    quality_inspector,
    report_writer
)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_spore_flow_user_query_to_final_response():
    """Test complete Spore message flow from user query to final response."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_manufacturing_advisor_to_analytics_specialist_flow():
    """Test Manufacturing Advisor enriches and passes to Analytics Specialist."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_parallel_execution_viz_and_quality():
    """Test Visualization and Quality Inspector run in parallel."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_session_id_correlation_across_agents():
    """Test session_id is maintained across all agents."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_failure_graceful_degradation():
    """Test system continues when one agent fails."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_timeout_handling_30s_limit():
    """Test timeout handling when agent processing exceeds 30 seconds."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_spore_message_ordering():
    """Test Spore messages are processed in correct order."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_context_preservation_multirun():
    """Test conversation context is preserved across multiple messages."""
    # Test implementation...

# NEW ENHANCED TESTS

@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_error_recovery_and_retry():
    """Test agents can recover from transient errors."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_sessions_isolation():
    """Test multiple concurrent sessions don't interfere with each other."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_state_consistency():
    """Test agent state remains consistent during concurrent operations."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_queueing_under_load():
    """Test Spore message queue handles high load correctly."""
    # Test implementation...
```

**Checklist:**
- [ ] Test full Spore message flow (user_query → final_response)
- [ ] Test Manufacturing Advisor → Analytics Specialist flow
- [ ] Test Analytics Specialist → Viz + Quality parallel flow
- [ ] Test Viz + Quality → Report Writer flow
- [ ] Test session_id correlation across agents
- [ ] Test agent failure handling (one agent fails, system continues)
- [ ] Test timeout handling (30s limit)
- [ ] Test Spore message ordering
- [ ] **[NEW]** Test agent error recovery and retry logic
- [ ] **[NEW]** Test concurrent sessions isolation
- [ ] **[NEW]** Test agent state consistency under concurrent load
- [ ] **[NEW]** Test message queueing behavior under high load
- [ ] Run tests: `./venv/bin/pytest tests/integration/agents/ -v`

---

#### test_spore_messaging.py (8 tests - NEW)

**Location:** `tests/integration/agents/test_spore_messaging.py`

**Purpose:** Deep testing of Praval Spore message system

```python
"""Tests for Praval Spore messaging system."""
import pytest
from praval import Spore, get_reef

@pytest.mark.integration
def test_spore_creation_and_validation():
    """Test Spore message creation with all required fields."""
    # Test implementation...

@pytest.mark.integration
def test_spore_broadcast_to_all_subscribers():
    """Test Spore broadcast reaches all subscribed agents."""
    # Test implementation...

@pytest.mark.integration
def test_spore_filtering_by_type():
    """Test agents only receive Spores they subscribe to."""
    # Test implementation...

@pytest.mark.integration
def test_spore_correlation_id_tracking():
    """Test correlation IDs are maintained across Spore chain."""
    # Test implementation...

@pytest.mark.integration
def test_spore_timestamp_ordering():
    """Test Spores are processed in timestamp order."""
    # Test implementation...

@pytest.mark.integration
def test_spore_payload_serialization():
    """Test complex payloads serialize/deserialize correctly."""
    # Test implementation...

@pytest.mark.integration
def test_spore_error_propagation():
    """Test errors in Spore processing propagate correctly."""
    # Test implementation...

@pytest.mark.integration
def test_spore_dead_letter_queue():
    """Test failed Spores are moved to dead letter queue."""
    # Test implementation...
```

**Checklist:**
- [ ] Test Spore creation and validation
- [ ] Test broadcast to all subscribers
- [ ] Test filtering by message type
- [ ] Test correlation ID tracking
- [ ] Test timestamp ordering
- [ ] Test payload serialization/deserialization
- [ ] Test error propagation
- [ ] Test dead letter queue for failed messages

---

#### test_reef_coordination.py (6 tests - NEW)

**Location:** `tests/integration/agents/test_reef_coordination.py`

**Purpose:** Test Praval Reef agent coordination

```python
"""Tests for Praval Reef agent coordination."""
import pytest
from reef_config import initialize_reef, cleanup_reef

@pytest.mark.integration
def test_reef_initialization():
    """Test Reef initializes all agents correctly."""
    # Test implementation...

@pytest.mark.integration
def test_reef_agent_registration():
    """Test agents register with Reef on startup."""
    # Test implementation...

@pytest.mark.integration
def test_reef_message_routing():
    """Test Reef routes messages to correct agents."""
    # Test implementation...

@pytest.mark.integration
def test_reef_health_monitoring():
    """Test Reef monitors agent health."""
    # Test implementation...

@pytest.mark.integration
def test_reef_cleanup_on_shutdown():
    """Test Reef cleans up resources on shutdown."""
    # Test implementation...

@pytest.mark.integration
def test_reef_agent_deregistration():
    """Test agents can deregister from Reef."""
    # Test implementation...
```

**Checklist:**
- [ ] Test Reef initialization
- [ ] Test agent registration
- [ ] Test message routing
- [ ] Test health monitoring
- [ ] Test cleanup on shutdown
- [ ] Test agent deregistration

---

### Day 10: dbt Business Logic Tests (Enhanced)

#### Custom dbt Tests (8 SQL tests - enhanced from 5)

**Location:** `dbt_transform/tests/`

**Files to create:**

1. **assert_oee_calculation_accurate.sql** (Enhanced)
```sql
-- Test OEE calculation matches formula: Availability × Performance × Quality
SELECT
    part_id,
    oee,
    availability,
    performance,
    quality_rate,
    (availability * performance * quality_rate) as calculated_oee,
    ABS(oee - (availability * performance * quality_rate)) as difference
FROM {{ ref('fact_press_operations') }}
WHERE ABS(oee - (availability * performance * quality_rate)) > 0.001
HAVING COUNT(*) > 0
```

2. **assert_pass_rate_matches_raw_data.sql**
```sql
-- Test pass_rate calculation matches raw data
SELECT
    date_key,
    part_family,
    pass_rate,
    passed_count,
    total_count,
    (passed_count::FLOAT / NULLIF(total_count, 0)) as calculated_pass_rate,
    ABS(pass_rate - (passed_count::FLOAT / NULLIF(total_count, 0))) as difference
FROM {{ ref('fact_press_operations') }}
WHERE total_count > 0
  AND ABS(pass_rate - (passed_count::FLOAT / NULLIF(total_count, 0))) > 0.001
HAVING COUNT(*) > 0
```

3. **assert_cost_calculations_correct.sql**
```sql
-- Test total_cost = material_cost + labor_cost + energy_cost
SELECT
    part_id,
    total_cost,
    material_cost,
    labor_cost,
    energy_cost,
    (material_cost + labor_cost + energy_cost) as calculated_total,
    ABS(total_cost - (material_cost + labor_cost + energy_cost)) as difference
FROM {{ ref('fact_press_operations') }}
WHERE ABS(total_cost - (material_cost + labor_cost + energy_cost)) > 0.01
HAVING COUNT(*) > 0
```

4. **assert_no_orphaned_records.sql**
```sql
-- Test no orphaned records in fact table
SELECT
    'press_operations' as table_name,
    COUNT(*) as orphaned_count
FROM {{ ref('fact_press_operations') }} f
LEFT JOIN {{ ref('stg_press_line_a_production') }} a ON f.part_id = a.id
LEFT JOIN {{ ref('stg_press_line_b_production') }} b ON f.part_id = b.id
WHERE a.id IS NULL AND b.id IS NULL
HAVING COUNT(*) > 0
```

5. **assert_grain_press_operations.sql**
```sql
-- Test fact table grain: one row per part produced
SELECT
    part_id,
    COUNT(*) as row_count
FROM {{ ref('fact_press_operations') }}
GROUP BY part_id
HAVING COUNT(*) > 1
```

6. **assert_date_range_consistency.sql** (NEW)
```sql
-- Test date ranges are consistent across all tables
WITH date_ranges AS (
    SELECT
        'press_operations' as table_name,
        MIN(production_date) as min_date,
        MAX(production_date) as max_date
    FROM {{ ref('fact_press_operations') }}
    UNION ALL
    SELECT
        'part_family_performance' as table_name,
        MIN(analysis_date) as min_date,
        MAX(analysis_date) as max_date
    FROM {{ ref('agg_part_family_performance') }}
)
SELECT *
FROM date_ranges
WHERE DATEDIFF(day, min_date, max_date) < 0
   OR min_date IS NULL
   OR max_date IS NULL
```

7. **assert_no_duplicate_keys.sql** (NEW)
```sql
-- Test all surrogate keys are unique
{% set tables = [
    'fact_press_operations',
    'fact_production_quality',
    'agg_part_family_performance'
] %}

{% for table in tables %}
SELECT
    '{{ table }}' as table_name,
    'Duplicate keys found' as error_message
FROM (
    SELECT
        COUNT(*) as dup_count
    FROM {{ ref(table) }}
    GROUP BY 1
    HAVING COUNT(*) > 1
) duplicates
WHERE dup_count > 0
{% if not loop.last %}UNION ALL{% endif %}
{% endfor %}
```

8. **assert_metric_bounds.sql** (NEW)
```sql
-- Test metrics are within expected bounds
SELECT
    'oee_out_of_bounds' as error_type,
    COUNT(*) as error_count
FROM {{ ref('fact_press_operations') }}
WHERE oee < 0 OR oee > 1

UNION ALL

SELECT
    'pass_rate_out_of_bounds' as error_type,
    COUNT(*) as error_count
FROM {{ ref('fact_press_operations') }}
WHERE pass_rate < 0 OR pass_rate > 1

UNION ALL

SELECT
    'negative_costs' as error_type,
    COUNT(*) as error_count
FROM {{ ref('fact_press_operations') }}
WHERE total_cost < 0 OR material_cost < 0 OR labor_cost < 0 OR energy_cost < 0

HAVING SUM(error_count) > 0
```

**Checklist:**
- [ ] Test OEE = Availability × Performance × Quality
- [ ] Test pass_rate = passed_count / total_count
- [ ] Test total_cost = material + labor + energy
- [ ] Test fact table grain (one row per part)
- [ ] Test referential integrity (no orphaned records)
- [ ] **[NEW]** Test date range consistency across tables
- [ ] **[NEW]** Test no duplicate surrogate keys
- [ ] **[NEW]** Test metrics within expected bounds
- [ ] Run tests: `docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform`

---

### Day 11: Cube.js Schema Validation (Enhanced)

#### test_cubejs_schemas.py (10 tests - enhanced from 7)

**Location:** `tests/integration/cubejs/test_cubejs_schemas.py`

```python
"""Integration tests for Cube.js schema validation."""
import pytest
from agents.cubejs_client import cubejs_client
from agents.models import CubeQuery

@pytest.mark.integration
@pytest.mark.asyncio
async def test_press_operations_cube_query():
    """Test PressOperations cube returns data correctly."""
    query = CubeQuery(
        measures=["PressOperations.count", "PressOperations.avgOee"],
        dimensions=["PressOperations.partFamily"]
    )
    result = await cubejs_client.execute_query(query)
    assert "data" in result
    assert len(result["data"]) > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_part_family_performance_cube_query():
    """Test PartFamilyPerformance cube returns data correctly."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_press_line_utilization_cube_query():
    """Test PressLineUtilization cube returns data correctly."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_measure_calculations_match_expected():
    """Test measure calculations return expected values."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_filter_application_works_correctly():
    """Test filters are applied correctly to queries."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_time_dimension_queries():
    """Test time dimension queries work correctly."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_joins():
    """Test joins between cubes work correctly."""
    # Test implementation...

# NEW ENHANCED TESTS

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pre_aggregations_used():
    """Test queries use pre-aggregations when available."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_large_result_set_handling():
    """Test handling of large result sets (>10k rows)."""
    # Test implementation...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_meta_endpoint():
    """Test Cube.js meta endpoint returns schema information."""
    # Test implementation...
```

**Checklist:**
- [ ] Test PressOperations cube query
- [ ] Test PartFamilyPerformance cube query
- [ ] Test PressLineUtilization cube query
- [ ] Test measure calculations match expected results
- [ ] Test filter application works correctly
- [ ] Test time dimension queries
- [ ] Test joins between cubes
- [ ] **[NEW]** Test pre-aggregations are used
- [ ] **[NEW]** Test large result set handling
- [ ] **[NEW]** Test meta endpoint for schema info
- [ ] Run tests: `./venv/bin/pytest tests/integration/cubejs/ -v`

---

### Day 12-13: Database and Error Recovery Tests

#### Enhanced Database Tests

**Location:** `tests/integration/database/test_database_advanced.py`

```python
"""Advanced database integration tests."""
import pytest
from el_pipeline.database import DatabaseConnection

@pytest.mark.integration
def test_connection_pool_exhaustion():
    """Test behavior when connection pool is exhausted."""
    # Test implementation...

@pytest.mark.integration
def test_transaction_rollback_on_error():
    """Test transactions rollback correctly on error."""
    # Test implementation...

@pytest.mark.integration
def test_deadlock_detection_and_retry():
    """Test deadlock detection and automatic retry."""
    # Test implementation...

@pytest.mark.integration
def test_connection_recovery_after_timeout():
    """Test connection can recover after timeout."""
    # Test implementation...

@pytest.mark.integration
def test_concurrent_writes():
    """Test concurrent write operations don't cause conflicts."""
    # Test implementation...

@pytest.mark.integration
def test_query_cancellation():
    """Test long-running queries can be cancelled."""
    # Test implementation...
```

**Checklist:**
- [ ] Test connection pool exhaustion
- [ ] Test transaction rollback on error
- [ ] Test deadlock detection and retry
- [ ] Test connection recovery after timeout
- [ ] Test concurrent write operations
- [ ] Test query cancellation

---

### Day 14: CLI and Airflow Tests (Enhanced)

#### test_cli.py (6 tests - enhanced from 4)

**Location:** `tests/unit/el_pipeline/test_cli.py`

```python
"""Tests for EL pipeline CLI."""
import pytest
from click.testing import CliRunner
from el_pipeline.cli import main, run_full_sync, check_warehouse

def test_sync_command_execution():
    """Test 'sync' command executes successfully."""
    runner = CliRunner()
    result = runner.invoke(main, ['sync'])
    assert result.exit_code == 0

def test_check_command_execution():
    """Test 'check' command executes successfully."""
    # Test implementation...

def test_invalid_command():
    """Test invalid command shows help."""
    # Test implementation...

def test_sync_with_error_handling():
    """Test sync command handles errors gracefully."""
    # Test implementation...

# NEW TESTS

def test_cli_logging_output():
    """Test CLI logging outputs correctly."""
    # Test implementation...

def test_cli_exit_codes():
    """Test CLI returns correct exit codes for different scenarios."""
    # Test implementation...
```

#### test_dags.py (6 tests - enhanced from 4)

**Location:** `tests/unit/airflow/test_dags.py`

```python
"""Tests for Airflow DAGs."""
import pytest
from airflow.models import DagBag

def test_dag_imports_successfully():
    """Test DAG imports without errors."""
    dag_bag = DagBag(include_examples=False)
    assert len(dag_bag.import_errors) == 0

def test_task_dependencies_correct():
    """Test task dependencies are configured correctly."""
    # Test implementation...

def test_schedule_interval_set():
    """Test schedule interval is properly set."""
    # Test implementation...

def test_default_args_configured():
    """Test default args are configured correctly."""
    # Test implementation...

# NEW TESTS

def test_dag_has_tags():
    """Test DAG has appropriate tags for filtering."""
    # Test implementation...

def test_task_timeout_configured():
    """Test tasks have appropriate timeout settings."""
    # Test implementation...
```

---

## Phase 3: Advanced Testing & Quality (Week 3, Days 15-21)

### Objectives
- Integrate property-based testing with Hypothesis
- Add mutation testing for test quality validation
- Implement security scanning
- Enhance test infrastructure
- **Target: 85% coverage**

---

### Day 15-16: Property-Based Testing

**Install Hypothesis:**
```bash
./venv/bin/pip install hypothesis
```

#### test_property_based.py (NEW)

**Location:** `tests/unit/property/test_property_based.py`

```python
"""Property-based tests using Hypothesis."""
import pytest
from hypothesis import given, strategies as st
from el_pipeline.database import DatabaseConnection
from agents.manufacturing_advisor import ManufacturingAdvisorAgent

@given(st.floats(min_value=0.0, max_value=1.0),
       st.floats(min_value=0.0, max_value=1.0),
       st.floats(min_value=0.0, max_value=1.0))
def test_oee_calculation_properties(availability, performance, quality):
    """Test OEE calculation properties hold for all valid inputs."""
    oee = availability * performance * quality
    assert 0.0 <= oee <= 1.0
    assert oee <= min(availability, performance, quality)

@given(st.integers(min_value=0, max_value=10000),
       st.integers(min_value=0, max_value=10000))
def test_pass_rate_calculation_properties(passed, total):
    """Test pass rate calculation properties."""
    if total == 0:
        pass_rate = 0.0
    else:
        pass_rate = passed / total
    assert 0.0 <= pass_rate <= 1.0
    if passed == total:
        assert pass_rate == 1.0

@given(st.text(min_size=1, max_size=200))
def test_query_enrichment_handles_any_text(query_text):
    """Test query enrichment handles any text input without crashing."""
    # Test that agent doesn't crash on any input
    # This tests robustness

@given(st.lists(st.dictionaries(
    st.text(),
    st.one_of(st.text(), st.integers(), st.floats()),
    min_size=1, max_size=10
)))
def test_data_loading_handles_various_structures(data_list):
    """Test data loading handles various data structures."""
    # Test implementation...
```

**Checklist:**
- [ ] Test OEE calculation properties
- [ ] Test pass rate calculation properties
- [ ] Test query enrichment robustness
- [ ] Test data loading with various structures
- [ ] Test cost calculations with edge cases
- [ ] Test timestamp handling properties
- [ ] Run: `./venv/bin/pytest tests/unit/property/ -v`

---

### Day 17: Mutation Testing

**Install mutmut:**
```bash
./venv/bin/pip install mutmut
```

**Configure mutation testing:**
```bash
# Run mutation testing on critical modules
mutmut run --paths-to-mutate=el_pipeline/loader.py
mutmut run --paths-to-mutate=agents/manufacturing_advisor.py
mutmut run --paths-to-mutate=agents/analytics_specialist.py

# View results
mutmut results
mutmut html
```

**Mutation Testing Checklist:**
- [ ] Run mutation testing on el_pipeline/loader.py
- [ ] Run mutation testing on agents/manufacturing_advisor.py
- [ ] Run mutation testing on agents/analytics_specialist.py
- [ ] Achieve >80% mutation score
- [ ] Fix surviving mutants with additional tests
- [ ] Document mutation testing results

---

### Day 18: Security Scanning

**Install security tools:**
```bash
./venv/bin/pip install bandit safety
```

#### test_security.py (NEW)

**Location:** `tests/security/test_security.py`

```python
"""Security tests."""
import pytest
import subprocess

def test_bandit_security_scan():
    """Run bandit security scan on codebase."""
    result = subprocess.run(
        ['bandit', '-r', 'el_pipeline/', 'agents/', '-f', 'json'],
        capture_output=True,
        text=True
    )
    # Assert no high severity issues
    # Test implementation...

def test_dependency_vulnerabilities():
    """Check for known vulnerabilities in dependencies."""
    result = subprocess.run(
        ['safety', 'check', '--json'],
        capture_output=True,
        text=True
    )
    # Assert no critical vulnerabilities
    # Test implementation...

def test_secrets_not_hardcoded():
    """Test no secrets are hardcoded in source."""
    # Scan for patterns like API keys, passwords
    # Test implementation...
```

**Security Checklist:**
- [ ] Run bandit security scan
- [ ] Check for dependency vulnerabilities
- [ ] Scan for hardcoded secrets
- [ ] Test SQL injection vulnerabilities
- [ ] Test for insecure deserialization
- [ ] Verify secure defaults in configurations

---

### Day 19-20: Container and Infrastructure Tests

#### test_docker.py (NEW)

**Location:** `tests/integration/infrastructure/test_docker.py`

```python
"""Docker container integration tests."""
import pytest
import docker

@pytest.fixture
def docker_client():
    """Get Docker client."""
    return docker.from_env()

def test_all_containers_running(docker_client):
    """Test all required containers are running."""
    containers = docker_client.containers.list()
    required = ['analytics-agents', 'postgres-warehouse', 'cubejs', 'frontend']
    running = [c.name for c in containers]
    for req in required:
        assert any(req in name for name in running)

def test_container_health_checks(docker_client):
    """Test container health checks are passing."""
    # Test implementation...

def test_container_resource_limits():
    """Test containers have appropriate resource limits."""
    # Test implementation...

def test_container_restart_policy():
    """Test containers have correct restart policies."""
    # Test implementation...
```

**Infrastructure Checklist:**
- [ ] Test all containers are running
- [ ] Test container health checks
- [ ] Test resource limits configured
- [ ] Test restart policies
- [ ] Test network connectivity between containers
- [ ] Test volume mounts are correct

---

### Day 21: Test Infrastructure Hardening

**Enhanced test fixtures:**

```python
# tests/conftest.py enhancements

@pytest.fixture(scope="session")
def docker_services():
    """Ensure Docker services are running for tests."""
    # Implementation...

@pytest.fixture
def mock_llm_responses():
    """Provide realistic mock LLM responses."""
    return {
        "manufacturing_advisor": {
            "in_scope": {...},
            "out_of_scope": {...}
        },
        # More mocked responses...
    }

@pytest.fixture
def sample_press_data_large():
    """Provide large sample dataset for performance tests."""
    return PressOperationFactory.create_batch(10000)
```

**Checklist:**
- [ ] Create session-scoped fixtures for Docker services
- [ ] Create comprehensive mock LLM response library
- [ ] Create large data fixtures for performance testing
- [ ] Add fixture for database seeding
- [ ] Add fixture for cleanup after tests

---

## Phase 4: Frontend, E2E & Performance (Week 4, Days 22-28)

### Objectives
- Implement comprehensive frontend tests
- Build full E2E test suite
- Add performance and load testing
- Add chaos engineering tests
- **Target: 90%+ coverage, critical modules 95%+**

---

### Day 22-23: Frontend Testing (Enhanced)

#### Jest Configuration

**Install dependencies:**
```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom @testing-library/react-hooks
```

**Create jest.config.js:**
```javascript
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 88,
      functions: 88,
      lines: 88,
      statements: 88,
    },
  },
};
```

#### Component Tests (15 tests)

**Location:** `frontend/src/components/__tests__/`

```javascript
// ChatInterface.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../ChatInterface';

describe('ChatInterface', () => {
  test('renders chat input', () => {
    render(<ChatInterface />);
    expect(screen.getByPlaceholderText(/ask a question/i)).toBeInTheDocument();
  });

  test('sends message on submit', async () => {
    const mockSend = jest.fn();
    render(<ChatInterface onSendMessage={mockSend} />);

    const input = screen.getByPlaceholderText(/ask a question/i);
    fireEvent.change(input, { target: { value: 'test query' } });
    fireEvent.submit(input.closest('form'));

    await waitFor(() => {
      expect(mockSend).toHaveBeenCalledWith('test query');
    });
  });

  test('displays response with chart', async () => {
    // Test implementation...
  });

  test('shows loading state during API call', () => {
    // Test implementation...
  });

  test('handles API errors gracefully', () => {
    // Test implementation...
  });

  // 10 more tests...
});

// BarChart.test.tsx
// LineChart.test.tsx
// InsightsList.test.tsx
```

#### Integration Tests (8 tests - NEW)

**Location:** `frontend/src/__tests__/integration/`

```javascript
// api.integration.test.ts
describe('API Integration', () => {
  test('fetches data from agents API', async () => {
    // Test implementation...
  });

  test('handles authentication', async () => {
    // Test implementation...
  });

  test('retries on network failure', async () => {
    // Test implementation...
  });

  // 5 more tests...
});
```

**Frontend Testing Checklist:**
- [ ] Test ChatInterface renders correctly
- [ ] Test message sending
- [ ] Test response display with charts
- [ ] Test loading states
- [ ] Test error handling
- [ ] Test BarChart component
- [ ] Test LineChart component
- [ ] Test TableView component
- [ ] Test InsightsList component
- [ ] Test SessionInfo component
- [ ] Test SuggestedQuestions component
- [ ] Test API client integration
- [ ] Test authentication flows
- [ ] Test error retry logic
- [ ] Test state management
- [ ] Run: `npm test`

---

### Day 24: Playwright E2E Tests (8 tests)

**Install Playwright:**
```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install
```

**Location:** `frontend/e2e/`

```javascript
// chat-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Flow E2E', () => {
  test('complete chat interaction', async ({ page }) => {
    await page.goto('http://localhost:3000');

    // Type query
    await page.fill('[data-testid="chat-input"]', 'What is the OEE?');
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await expect(page.locator('[data-testid="chat-response"]')).toBeVisible({ timeout: 30000 });

    // Verify chart appears
    await expect(page.locator('canvas')).toBeVisible();
  });

  test('multi-turn conversation', async ({ page }) => {
    // Test implementation...
  });

  test('chart interaction and filtering', async ({ page }) => {
    // Test implementation...
  });

  test('session persistence across page reload', async ({ page }) => {
    // Test implementation...
  });

  test('error handling when backend is down', async ({ page }) => {
    // Test implementation...
  });

  test('keyboard navigation accessibility', async ({ page }) => {
    // Test implementation...
  });

  test('mobile responsive layout', async ({ page, viewport }) => {
    // Test implementation...
  });

  test('suggested questions interaction', async ({ page }) => {
    // Test implementation...
  });
});
```

**E2E Testing Checklist:**
- [ ] Test complete chat interaction
- [ ] Test multi-turn conversation
- [ ] Test chart interaction
- [ ] Test session persistence
- [ ] Test error handling
- [ ] Test keyboard navigation
- [ ] Test mobile responsive layout
- [ ] Test suggested questions
- [ ] Run: `npx playwright test`

---

### Day 25: Full Data Pipeline E2E Tests (10 tests)

**Location:** `tests/e2e/test_full_data_pipeline.py`

```python
"""Full data pipeline E2E tests."""
import pytest
import time
from el_pipeline.pipeline import ELPipeline

@pytest.mark.e2e
def test_source_to_warehouse_data_flow(test_config):
    """Test data flows from source DBs to warehouse."""
    pipeline = ELPipeline(test_config)

    # Run EL sync
    stats = pipeline.run_full_sync()
    assert stats['refills_count'] > 0

    # Verify data in warehouse
    warehouse_stats = pipeline.get_warehouse_stats()
    assert warehouse_stats['refills_count'] == stats['refills_count']

@pytest.mark.e2e
def test_warehouse_to_dbt_to_marts():
    """Test dbt transforms warehouse data to marts."""
    # Run dbt
    # Verify mart tables populated
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_marts_to_cubejs_queries():
    """Test Cube.js queries work on mart tables."""
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_cubejs_to_agents_to_response():
    """Test agents can query Cube.js and generate responses."""
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_turn_conversation_full_stack():
    """Test multi-turn conversation through full stack."""
    # Test implementation...

@pytest.mark.e2e
def test_session_persistence_across_restarts():
    """Test session data persists across service restarts."""
    # Test implementation...

@pytest.mark.e2e
def test_error_recovery_full_pipeline():
    """Test system recovers from various failure scenarios."""
    # Test implementation...

@pytest.mark.e2e
def test_data_quality_end_to_end():
    """Test data quality is maintained through entire pipeline."""
    # Test implementation...

@pytest.mark.e2e
def test_real_time_data_updates():
    """Test system handles real-time data updates."""
    # Test implementation...

@pytest.mark.e2e
def test_concurrent_user_sessions():
    """Test multiple concurrent user sessions work correctly."""
    # Test implementation...
```

**E2E Pipeline Checklist:**
- [ ] Test: Source DB → EL → Warehouse
- [ ] Test: Warehouse → dbt → Marts
- [ ] Test: Marts → Cube.js queries
- [ ] Test: Cube.js → Agents → Response
- [ ] Test: Multi-turn conversation
- [ ] Test: Session persistence
- [ ] Test: Error recovery
- [ ] Test: Data quality end-to-end
- [ ] Test: Real-time data updates
- [ ] Test: Concurrent user sessions
- [ ] Run: `./venv/bin/pytest tests/e2e/ -v --timeout=600`

---

### Day 26: Performance Tests (8 tests)

**Install locust:**
```bash
./venv/bin/pip install locust pytest-benchmark
```

**Location:** `tests/performance/test_load.py`

```python
"""Performance and load tests."""
import pytest
from locust import HttpUser, task, between

class AgentsLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def query_oee(self):
        self.client.post("/chat", json={
            "message": "What's the OEE?",
            "session_id": f"load-test-{self.user_id}"
        })

@pytest.mark.benchmark
def test_query_enrichment_performance(benchmark):
    """Benchmark query enrichment performance."""
    # Test implementation...

@pytest.mark.benchmark
def test_data_loading_performance(benchmark):
    """Benchmark data loading for large datasets."""
    # Test implementation...

@pytest.mark.benchmark
def test_cubejs_query_performance(benchmark):
    """Benchmark Cube.js query execution."""
    # Test implementation...

@pytest.mark.performance
def test_concurrent_users_10():
    """Test system with 10 concurrent users."""
    # Test implementation...

@pytest.mark.performance
def test_concurrent_users_50():
    """Test system with 50 concurrent users."""
    # Test implementation...

@pytest.mark.performance
def test_large_result_set_10k_rows():
    """Test handling of large result sets."""
    # Test implementation...

@pytest.mark.performance
def test_agent_response_latency():
    """Test agent response latency under load."""
    # Test implementation...

@pytest.mark.performance
def test_database_connection_pool():
    """Test database connection pool under stress."""
    # Test implementation...
```

**Performance Testing Checklist:**
- [ ] Test 10 concurrent users
- [ ] Test 50 concurrent users
- [ ] Test large result sets (>10k rows)
- [ ] Test agent response latency
- [ ] Test database connection pool
- [ ] Benchmark query enrichment
- [ ] Benchmark data loading
- [ ] Benchmark Cube.js queries
- [ ] Run: `./venv/bin/pytest tests/performance/ -v`
- [ ] Run: `locust -f tests/performance/locustfile.py`

---

### Day 27: Chaos Engineering Tests (6 tests - NEW)

**Location:** `tests/e2e/test_chaos_engineering.py`

```python
"""Chaos engineering tests."""
import pytest
import docker

@pytest.mark.e2e
@pytest.mark.chaos
def test_database_container_restart():
    """Test system recovers from database restart."""
    client = docker.from_env()

    # Restart database
    container = client.containers.get('postgres-warehouse')
    container.restart()

    # Test system recovers
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.chaos
def test_agents_container_crash():
    """Test system handles agents container crash."""
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.chaos
def test_network_partition():
    """Test system handles network partitions."""
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.chaos
def test_slow_database_responses():
    """Test system handles slow database responses."""
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.chaos
def test_cubejs_service_unavailable():
    """Test system handles Cube.js unavailability."""
    # Test implementation...

@pytest.mark.e2e
@pytest.mark.chaos
def test_openai_api_timeout():
    """Test system handles OpenAI API timeouts."""
    # Test implementation...
```

**Chaos Engineering Checklist:**
- [ ] Test database container restart
- [ ] Test agents container crash
- [ ] Test network partition
- [ ] Test slow database responses
- [ ] Test Cube.js unavailability
- [ ] Test OpenAI API timeout

---

### Day 28: Data Quality E2E Tests (8 tests - NEW)

**Location:** `tests/e2e/test_data_quality_e2e.py`

```python
"""End-to-end data quality tests."""
import pytest

@pytest.mark.e2e
def test_source_data_integrity():
    """Test source data maintains integrity through pipeline."""
    # Test implementation...

@pytest.mark.e2e
def test_aggregation_accuracy():
    """Test aggregations are mathematically accurate."""
    # Test implementation...

@pytest.mark.e2e
def test_no_data_loss():
    """Test no data is lost through pipeline."""
    # Test implementation...

@pytest.mark.e2e
def test_timestamp_consistency():
    """Test timestamps are consistent across all stages."""
    # Test implementation...

@pytest.mark.e2e
def test_referential_integrity_end_to_end():
    """Test referential integrity maintained end-to-end."""
    # Test implementation...

@pytest.mark.e2e
def test_data_type_consistency():
    """Test data types remain consistent."""
    # Test implementation...

@pytest.mark.e2e
def test_null_handling_consistency():
    """Test NULL values handled consistently."""
    # Test implementation...

@pytest.mark.e2e
def test_semantic_layer_accuracy():
    """Test semantic layer calculations match raw data."""
    # Test implementation...
```

**Data Quality Checklist:**
- [ ] Test source data integrity
- [ ] Test aggregation accuracy
- [ ] Test no data loss
- [ ] Test timestamp consistency
- [ ] Test referential integrity
- [ ] Test data type consistency
- [ ] Test NULL handling
- [ ] Test semantic layer accuracy

---

## Updated Test Count Summary

### By Phase
- **Phase 1:** 84 tests (vs 60 original)
- **Phase 2:** 56 tests (vs 28 original)
- **Phase 3:** Infrastructure + security tests
- **Phase 4:** 63 tests (vs 26 original)

### Total: 203+ tests (vs 114+ original)

### By Module
- **EL Pipeline:** 26 tests (target: 95% coverage)
- **Agents:** 78 tests (target: 92% coverage)
- **dbt:** 8 SQL tests (target: 90% coverage)
- **Cube.js:** 10 tests (target: 85% coverage)
- **Frontend:** 23 tests (target: 88% coverage)
- **E2E:** 32 tests (full coverage)
- **Performance:** 14 tests
- **Infrastructure:** 12 tests

---

## Success Metrics (Updated)

### Quantitative
- **Test Count:** 19 → 203+ (970% increase)
- **Overall Coverage:** 25% → 90%+
- **Critical Modules:** 70% → 95%+
- **Test Execution:** < 10 minutes
- **CI/CD Reliability:** 98%+

### Qualitative
- Property-based testing integrated
- Mutation testing validates test quality
- Security scanning automated
- Chaos engineering validates resilience
- Performance benchmarks established

---

## Maintenance Plan

### Weekly
- Review coverage reports
- Fix flaky tests
- Update mocks for external services

### Monthly
- Run mutation testing
- Update security scans
- Review performance benchmarks
- Optimize slow tests

### Per Release
- Full E2E test suite
- Chaos engineering tests
- Performance regression tests
- Security audit

---

## Resources

- **Hypothesis docs:** https://hypothesis.readthedocs.io/
- **mutmut docs:** https://mutmut.readthedocs.io/
- **Playwright docs:** https://playwright.dev/
- **Locust docs:** https://locust.io/
- **Bandit docs:** https://bandit.readthedocs.io/

---

**End of Detailed Plan for Phases 2-4**
