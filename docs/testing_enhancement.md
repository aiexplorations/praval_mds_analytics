# Testing Enhancement Report
## Praval Manufacturing Analytics System

**Report Date:** 2025-11-12
**Objective:** Comprehensive analysis of test coverage at module and end-to-end levels

---

## Executive Summary

### Current State
- **Total Test Functions:** 19 (6 in el_pipeline, 13 in agents)
- **Test Coverage:** Limited to basic unit tests and integration tests
- **Primary Gaps:** Agent logic, frontend, Cube.js, Airflow, and end-to-end flows

### Coverage by Component
| Component | Unit Tests | Integration Tests | E2E Tests | Status |
|-----------|------------|-------------------|-----------|--------|
| EL Pipeline | ✅ Good | ✅ Good | ❌ None | **70%** |
| Agents Backend | ⚠️ Minimal | ❌ None | ❌ None | **15%** |
| dbt Models | ⚠️ Schema Only | ❌ None | ❌ None | **20%** |
| Cube.js | ❌ None | ❌ None | ❌ None | **0%** |
| Frontend | ❌ None | ❌ None | ❌ None | **0%** |
| Airflow | ❌ None | ❌ None | ❌ None | **0%** |
| **Overall** | **⚠️ Partial** | **⚠️ Minimal** | **❌ None** | **25%** |

---

## Detailed Analysis

### 1. EL Pipeline Module ✅ **Good Coverage (70%)**

#### What's Tested (tests/el_pipeline/)

**test_config.py** (5 tests)
- ✅ DatabaseConfig creation and attribute validation
- ✅ Connection string generation
- ✅ PipelineConfig creation with multiple databases
- ✅ Default value handling (batch_size, log_level)

**test_database.py** (6 tests, all marked @pytest.mark.integration)
- ✅ Database connection establishment
- ✅ Connection closing
- ✅ Query execution
- ✅ Table row count retrieval
- ✅ Cursor context manager
- ✅ Connection reuse

**test_extractor.py** (5 tests, all integration)
- ✅ RefillsExtractor data extraction
- ✅ BodiesExtractor data extraction
- ✅ SpringsExtractor data extraction
- ✅ Max timestamp retrieval
- ✅ Incremental extraction

**test_pipeline.py** (3 tests, all integration)
- ✅ Full sync execution
- ✅ Warehouse statistics retrieval
- ✅ Connection cleanup

#### What's NOT Tested

**loader.py** (0 tests) ❌ **CRITICAL GAP**
- ❌ load_refills() function
- ❌ load_bodies() function
- ❌ load_springs() function
- ❌ Truncate table functionality
- ❌ Batch insert error handling
- ❌ Data validation before loading
- ❌ Timestamp handling (_airbyte_emitted_at)

**cli.py** (0 tests) ❌
- ❌ CLI argument parsing
- ❌ run_full_sync() command
- ❌ check_warehouse() command
- ❌ Error handling and user feedback
- ❌ Rich console output formatting

**Error Scenarios** (0 tests) ❌ **HIGH PRIORITY**
- ❌ Connection failures (timeouts, refused connections)
- ❌ Malformed data handling
- ❌ Missing columns in source data
- ❌ Data type mismatches
- ❌ Transaction rollback scenarios
- ❌ Partial sync failures
- ❌ Resource exhaustion (memory, disk space)

**Edge Cases** (0 tests)
- ❌ Empty table extraction
- ❌ Very large batch processing
- ❌ Duplicate data handling
- ❌ NULL value handling in various columns
- ❌ Special characters in string fields

**Performance** (0 tests)
- ❌ Large dataset extraction (>100k rows)
- ❌ Batch size optimization
- ❌ Memory usage profiling
- ❌ Connection pool stress testing

**conftest.py Enhancement Needs**
- ⚠️ Fixtures hardcode localhost ports (brittle for CI/CD)
- ⚠️ No mock database fixtures for pure unit tests
- ⚠️ No test data factory/builders

---

### 2. Agents Backend ⚠️ **Minimal Coverage (15%)**

#### What's Tested (agents/tests/)

**test_session_manager.py** (8 tests, all unit)
- ✅ Session creation and UUID generation
- ✅ Message addition to sessions
- ✅ Context retrieval with max_messages limit
- ✅ Message history truncation
- ✅ Session existence checking
- ✅ Expired session cleanup

**test_api.py** (5 tests, using FastAPI TestClient with mocks)
- ✅ Root endpoint response
- ✅ Health check endpoint with Cube.js status
- ✅ Chat endpoint validation errors
- ✅ Session creation via chat
- ✅ Session deletion

#### What's NOT Tested ❌ **CRITICAL GAPS**

**manufacturing_advisor.py** (0 tests) ❌ **HIGH PRIORITY**
- ❌ enrich_query() function
- ❌ Guardrails for out-of-scope queries
- ❌ Manufacturing terminology extraction
- ❌ Part family/metric/dimension extraction
- ❌ Cube recommendation logic
- ❌ Context handling from previous messages
- ❌ LLM response parsing
- ❌ Error handling when OpenAI API fails
- ❌ Prompt engineering validation

**analytics_specialist.py** (0 tests) ❌ **HIGH PRIORITY**
- ❌ Query translation from enriched requests
- ❌ Metric mapping (METRIC_MAPPING dict)
- ❌ Dimension mapping (DIMENSION_MAPPING dict)
- ❌ Cube selection logic
- ❌ Filter application
- ❌ Time range handling
- ❌ Cube.js query execution
- ❌ Result data processing
- ❌ Error handling for invalid queries
- ❌ Spore message creation and broadcasting

**visualization_specialist.py** (0 tests) ❌ **HIGH PRIORITY**
- ❌ Chart type selection logic
- ❌ Data formatting for Chart.js
- ❌ Bar chart data structure
- ❌ Line chart data structure
- ❌ Table data structure
- ❌ Data slicing/dicing for visualization
- ❌ Color scheme application
- ❌ Chart options generation
- ❌ Handling of empty datasets

**quality_inspector.py** (0 tests) ❌ **HIGH PRIORITY**
- ❌ Anomaly detection logic
- ❌ Statistical analysis functions
- ❌ Pattern recognition
- ❌ Root cause hypothesis generation
- ❌ Manufacturing domain expertise application
- ❌ Parallel execution with visualization specialist

**report_writer.py** (0 tests) ❌ **HIGH PRIORITY**
- ❌ Narrative composition from data and insights
- ❌ Actionable recommendations generation
- ❌ Follow-up question suggestions
- ❌ Final response assembly
- ❌ Response storage in _pending_responses
- ❌ Session correlation

**cubejs_client.py** (0 tests) ❌ **CRITICAL**
- ❌ execute_query() with valid queries
- ❌ HTTP error handling (4xx, 5xx)
- ❌ Connection errors (timeout, refused)
- ❌ get_meta() for schema introspection
- ❌ health_check() functionality
- ❌ Query serialization (Pydantic model_dump)
- ❌ Response parsing

**spore_schemas.py** (0 tests) ❌
- ❌ UserQuerySpore validation
- ❌ EnrichedRequestSpore validation
- ❌ QueryResultsSpore validation
- ❌ VisualizationSpore validation
- ❌ QualityInsightsSpore validation
- ❌ FinalResponseReadySpore validation
- ❌ Pydantic validation errors

**reef_config.py** (0 tests) ❌
- ❌ Reef initialization
- ❌ Agent registration
- ❌ Message routing
- ❌ Cleanup functionality

**app.py** (partially tested)
- ⚠️ Praval multi-agent orchestration
- ❌ Timeout handling (30s wait loop)
- ❌ Response polling logic
- ❌ Fallback response generation
- ❌ Lifespan context manager (startup/shutdown)
- ❌ CORS middleware configuration

**Integration Testing Gaps** ❌ **CRITICAL**
- ❌ Multi-agent collaboration flow
- ❌ Spore message passing between agents
- ❌ End-to-end: user_query → final_response
- ❌ Agent failure handling (graceful degradation)
- ❌ Parallel execution (Viz + Quality)
- ❌ Session state consistency across agents
- ❌ LLM error handling and retries

---

### 3. dbt Transformations ⚠️ **Schema Tests Only (20%)**

#### What's Tested (dbt_transform/models/)

**staging/schema.yml**
- ✅ stg_refills_production: unique, not_null, accepted_values
- ✅ stg_bodies_production: unique, not_null, accepted_values, material types
- ✅ stg_springs_production: unique, not_null, accepted_values

**marts/schema.yml**
- ✅ fact_production_quality: unique, not_null, accepted_values for component_type
- ✅ agg_component_quality_trends: pass_rate range validation
- ✅ agg_material_performance: unique material, not_null pass_rate

#### What's NOT Tested ❌ **HIGH PRIORITY**

**Business Logic Tests** (0 tests)
- ❌ Aggregation correctness (fact_press_operations metrics)
- ❌ OEE calculation validation
- ❌ Pass rate calculation accuracy
- ❌ Cost calculations (material + labor + energy)
- ❌ First pass yield vs rework rate logic
- ❌ Time-based aggregations (hourly, daily)

**Data Transformation Accuracy** (0 tests)
- ❌ Staging transformations (data cleansing)
- ❌ Intermediate model logic (int_automotive_production_combined)
- ❌ Mart model aggregations
- ❌ Die changeover logic
- ❌ Shift categorization
- ❌ Weekend/weekday split

**Relationship Tests** (0 tests)
- ❌ Foreign key relationships between facts and dimensions
- ❌ Referential integrity (press_line_id, die_id, etc.)
- ❌ Orphaned records detection

**Custom SQL Tests** (0 tests)
- ❌ Data completeness checks
- ❌ Historical data consistency
- ❌ Outlier detection
- ❌ Duplicate prevention
- ❌ Grain validation (one row per X)

**Incremental Model Tests** (0 tests)
- ❌ If any models are incremental, no tests for incremental logic

**Model Dependencies** (untested)
- ❌ Execution order validation
- ❌ Dependency DAG correctness

---

### 4. Cube.js Semantic Layer ❌ **No Tests (0%)**

#### What's NOT Tested ❌ **CRITICAL**

**Schema Definitions** (cubejs/schema/)
- ❌ PressOperations.js: measures, dimensions, joins
- ❌ PartFamilyPerformance.js: measures, dimensions
- ❌ PressLineUtilization.js: measures, dimensions
- ❌ Pre-aggregation configurations

**Measure Calculations**
- ❌ passRate formula validation
- ❌ avgOee calculation
- ❌ Cost aggregations (totalCost, avgCostPerPart)
- ❌ Complex calculations (firstPassYield, reworkRate)

**Dimension Mapping**
- ❌ SQL expressions for dimensions
- ❌ Joins to underlying tables
- ❌ Filter compatibility

**Query Execution**
- ❌ Sample queries against all cubes
- ❌ Filter application
- ❌ Time dimension queries
- ❌ Multi-cube queries

**Pre-aggregations**
- ❌ Build process validation
- ❌ Query routing to pre-aggs
- ❌ Refresh strategy

---

### 5. Frontend (Next.js) ❌ **No Tests (0%)**

#### What's NOT Tested ❌ **CRITICAL**

**Component Tests** (0 tests)
- ❌ ChatInterface component
- ❌ Chart components (Bar, Line, Table)
- ❌ InsightsList component
- ❌ SessionInfo component
- ❌ Props validation
- ❌ State management
- ❌ Event handlers

**Integration Tests** (0 tests)
- ❌ API client calls
- ❌ Response handling
- ❌ Error states
- ❌ Loading states

**E2E Tests** (0 tests)
- ❌ User flows (ask question → see chart)
- ❌ Multi-turn conversations
- ❌ Chart interactions
- ❌ Session management

**Accessibility** (0 tests)
- ❌ ARIA labels
- ❌ Keyboard navigation
- ❌ Screen reader compatibility

---

### 6. Airflow Orchestration ❌ **No Tests (0%)**

#### What's NOT Tested ❌ **HIGH PRIORITY**

**DAG Definitions** (airflow/dags/mds_pipeline_dag.py)
- ❌ DAG structure validation
- ❌ Task dependencies
- ❌ Schedule interval
- ❌ Default args
- ❌ Task timeout configuration

**Task Logic**
- ❌ EL pipeline task execution
- ❌ dbt run task
- ❌ dbt test task
- ❌ Error handling and retries
- ❌ Task failure notifications

**DAG Testing**
- ❌ Import errors
- ❌ Circular dependencies
- ❌ Task execution order

---

### 7. End-to-End Testing ❌ **No Tests (0%)**

#### Critical E2E Flows Missing ❌ **HIGHEST PRIORITY**

**Full Data Pipeline**
- ❌ Source DB → EL Pipeline → Warehouse
- ❌ Warehouse → dbt → Marts
- ❌ Marts → Cube.js → Query Results
- ❌ Query Results → Agents → Frontend
- ❌ Data quality validation at each stage

**Multi-Agent Conversation Flow**
```
User Query
  ↓
Manufacturing Advisor (enrich query)
  ↓
Analytics Specialist (translate + execute)
  ↓
Visualization Specialist + Quality Inspector (parallel)
  ↓
Report Writer (compose response)
  ↓
User receives: narrative + chart + insights + follow-ups
```
- ❌ Happy path flow
- ❌ Out-of-scope query rejection
- ❌ Data exploration queries
- ❌ Complex analytical queries
- ❌ Multi-turn conversations
- ❌ Context preservation across messages

**Agent Collaboration Scenarios**
- ❌ Successful parallel execution (Viz + Quality)
- ❌ Agent failure handling (one agent fails, system continues)
- ❌ Timeout scenarios (30s limit)
- ❌ Spore message ordering and correlation
- ❌ Session cleanup after conversation

**System Integration**
- ❌ Docker Compose stack health
- ❌ Service dependencies (Postgres → Cube.js → Agents)
- ❌ Network connectivity
- ❌ Container restart resilience

**Performance Under Load**
- ❌ Concurrent users (10, 50, 100)
- ❌ Large query results (>10k rows)
- ❌ Agent LLM call latency
- ❌ Memory usage over time
- ❌ Database connection pool exhaustion

**Data Quality Validation**
- ❌ Source data integrity checks
- ❌ Transformation accuracy end-to-end
- ❌ Semantic layer calculations vs raw data
- ❌ Frontend display vs API data

---

## Prioritized Testing Roadmap

### Phase 1: Critical Gaps (Weeks 1-2)

#### Priority 1A: Agent Unit Tests ⚠️ **BLOCKING**
**Effort:** 3-4 days
**Files to Create:**
- `agents/tests/test_manufacturing_advisor.py`
- `agents/tests/test_analytics_specialist.py`
- `agents/tests/test_visualization_specialist.py`
- `agents/tests/test_quality_inspector.py`
- `agents/tests/test_report_writer.py`
- `agents/tests/test_cubejs_client.py`

**Key Tests:**
- Mock OpenAI API responses
- Test query enrichment logic
- Test metric/dimension mapping
- Test chart type selection
- Test error handling for LLM failures
- Test Cube.js client with httpx mocks

#### Priority 1B: EL Pipeline Loader Tests ⚠️ **BLOCKING**
**Effort:** 1 day
**File:** `tests/el_pipeline/test_loader.py`

**Key Tests:**
- Test load_refills(), load_bodies(), load_springs()
- Test batch insert functionality
- Test truncate table
- Test error handling (duplicate keys, constraint violations)
- Test timestamp generation

#### Priority 1C: Basic E2E Smoke Test 🔥 **CRITICAL**
**Effort:** 2 days
**File:** `tests/e2e/test_basic_flow.py`

**Key Tests:**
- Test: user query → agent processing → response
- Test: simple data query flow
- Test: chart generation
- Mock external dependencies, test agent orchestration

### Phase 2: Integration Tests (Weeks 3-4)

#### Priority 2A: Multi-Agent Integration
**Effort:** 3 days
**File:** `tests/integration/test_agent_collaboration.py`

**Key Tests:**
- Test full Spore message flow
- Test parallel agent execution
- Test agent failure scenarios
- Test timeout handling

#### Priority 2B: dbt Business Logic Tests
**Effort:** 2 days
**Files:** `dbt_transform/tests/` (custom SQL tests)

**Key Tests:**
- Test OEE calculation accuracy
- Test aggregation correctness
- Test relationship integrity
- Test data completeness

#### Priority 2C: Cube.js Schema Validation
**Effort:** 2 days
**File:** `tests/integration/test_cubejs_schemas.py`

**Key Tests:**
- Test measure calculations
- Test sample queries against all cubes
- Test filter application
- Test dimension joins

### Phase 3: Expanded Coverage (Weeks 5-6)

#### Priority 3A: Frontend Component Tests
**Effort:** 3-4 days
**Framework:** Jest + React Testing Library

**Key Tests:**
- Test ChatInterface interactions
- Test chart rendering
- Test API client error handling
- Test loading/error states

#### Priority 3B: Airflow DAG Tests
**Effort:** 1 day
**File:** `tests/airflow/test_dags.py`

**Key Tests:**
- Test DAG import
- Test task dependencies
- Test task execution with mocks

#### Priority 3C: CLI Tests
**Effort:** 1 day
**File:** `tests/el_pipeline/test_cli.py`

**Key Tests:**
- Test argument parsing
- Test command execution
- Test error output
- Test Rich console formatting

### Phase 4: E2E and Performance (Weeks 7-8)

#### Priority 4A: Full E2E Test Suite
**Effort:** 5 days
**Files:** `tests/e2e/` directory

**Key Tests:**
- Test full data pipeline (source → frontend)
- Test multi-turn conversations
- Test error recovery
- Test session management
- Docker Compose stack tests

#### Priority 4B: Performance Tests
**Effort:** 3 days
**Files:** `tests/performance/`

**Tools:** pytest-benchmark, locust, or k6

**Key Tests:**
- Load test agents (concurrent requests)
- Test large query results
- Memory profiling
- Database connection pool stress test

#### Priority 4C: Data Quality Tests
**Effort:** 2 days
**Files:** `tests/data_quality/`

**Key Tests:**
- Source data validation
- End-to-end calculation accuracy
- Referential integrity checks

---

## Testing Infrastructure Enhancements

### Required Tooling

#### Python Testing
- **pytest-asyncio**: For async agent tests
- **pytest-mock**: For mocking OpenAI, Cube.js
- **pytest-httpx**: For testing httpx clients
- **pytest-cov**: Coverage reporting
- **factory-boy**: Test data factories
- **freezegun**: Time mocking for date-based tests

#### Frontend Testing
- **Jest**: Test runner
- **React Testing Library**: Component tests
- **Playwright** or **Cypress**: E2E tests
- **MSW (Mock Service Worker)**: API mocking

#### dbt Testing
- **dbt-expectations**: Extended test library
- **Custom SQL tests**: In `tests/` directory

#### Performance Testing
- **pytest-benchmark**: Microbenchmarks
- **locust**: Load testing
- **py-spy**: Python profiling

### CI/CD Pipeline

**Recommended GitHub Actions Workflow:**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    - EL pipeline unit tests
    - Agent unit tests
    - Coverage threshold: 90%

  integration-tests:
    - Spin up docker-compose
    - Run integration tests
    - dbt test

  e2e-tests:
    - Full stack E2E tests
    - Frontend E2E with Playwright

  data-quality:
    - dbt data quality tests
    - Cube.js query validation
```

### Test Data Management

**Needs:**
1. **Fixtures for Test Databases**
   - Seed data for source DBs (refills, bodies, springs)
   - Known good data for assertions
   - Edge case data (nulls, outliers, duplicates)

2. **Mock LLM Responses**
   - Canned OpenAI responses for predictable testing
   - Error responses for failure scenarios

3. **Test Configuration**
   - Separate .env.test file
   - Test-specific database ports
   - Dockerized test dependencies

---

## Coverage Metrics

### Current Coverage Estimate

**By Lines of Code (estimated):**
- EL Pipeline: ~70% (good unit + integration coverage)
- Agents: ~15% (only session manager and API endpoints)
- dbt: ~20% (schema tests only)
- Cube.js: 0%
- Frontend: 0%
- Airflow: 0%
- **Overall: ~25%**

### Target Coverage (Post-Roadmap)

**Recommended Targets:**
- EL Pipeline: 90%+ (critical data path)
- Agents: 85%+ (complex LLM logic, critical for user experience)
- dbt: 90%+ (business logic validation)
- Cube.js: 70%+ (schema validation)
- Frontend: 75%+ (component + integration tests)
- Airflow: 70%+ (DAG validation)
- **Overall Target: 90%+**

---

## Testing Best Practices Recommendations

### 1. Test Organization
```
tests/
├── unit/                    # Fast, isolated tests
│   ├── el_pipeline/
│   ├── agents/
│   └── dbt/
├── integration/             # Component interaction tests
│   ├── agent_collaboration/
│   ├── database/
│   └── cubejs/
├── e2e/                     # Full system tests
│   ├── data_pipeline/
│   ├── agent_flows/
│   └── frontend/
├── performance/             # Load and stress tests
└── conftest.py              # Shared fixtures
```

### 2. Test Naming Convention
```python
def test_<function_name>_<scenario>_<expected_outcome>():
    """
    Test that <function> does <expected> when <scenario>.
    """
```

Example:
```python
def test_enrich_query_out_of_scope_returns_rejection():
    """Test that enrich_query returns is_in_scope=False for weather questions."""
```

### 3. Fixture Strategy
- **Unit Tests:** Mock all external dependencies
- **Integration Tests:** Use real databases (Dockerized)
- **E2E Tests:** Full stack, minimal mocks

### 4. Continuous Testing
- Pre-commit hooks for fast unit tests
- PR checks for full test suite
- Nightly E2E and performance tests
- Weekly data quality validation

### 5. Test Documentation
- Each test file should have module docstring
- Complex tests should have comments explaining logic
- Maintain `docs/testing_guide.md` with examples

---

## Risk Assessment

### High-Risk Areas (Untested)

1. **Agent LLM Logic** 🔴 **CRITICAL**
   - **Risk:** Incorrect query enrichment leads to wrong answers
   - **Impact:** Poor user experience, incorrect analytics
   - **Mitigation:** Priority 1A tests

2. **Data Loading** 🔴 **CRITICAL**
   - **Risk:** Silent data loss or corruption
   - **Impact:** Analytics based on incomplete/wrong data
   - **Mitigation:** Priority 1B tests

3. **Multi-Agent Coordination** 🔴 **CRITICAL**
   - **Risk:** Agents don't communicate correctly
   - **Impact:** System fails or produces incomplete responses
   - **Mitigation:** Priority 2A tests

4. **dbt Business Logic** 🟡 **HIGH**
   - **Risk:** Incorrect aggregations or calculations
   - **Impact:** Wrong metrics (OEE, pass rates, costs)
   - **Mitigation:** Priority 2B tests

5. **Frontend** 🟡 **MEDIUM**
   - **Risk:** UI bugs, poor error handling
   - **Impact:** User confusion, accessibility issues
   - **Mitigation:** Priority 3A tests

---

## Step-by-Step Implementation Plan

### Overview: Test-First Deployment Strategy

**Objective:** Ensure all tests pass before deployment. No containers start if tests fail.

**Workflow:**
```
Code Changes → Unit Tests → Integration Tests → Build Containers → E2E Tests → Deploy
                   ↓              ↓                                    ↓
                 FAIL           FAIL                                 FAIL
                   ↓              ↓                                    ↓
                 STOP           STOP                                  STOP
```

---

## Phase 0: Testing Infrastructure Setup (Days 1-2)

### Checklist

#### Day 1: Dependencies and Configuration

- [ ] **Install Testing Dependencies**
  ```bash
  # Add to requirements.txt (root level)
  pytest==7.4.3
  pytest-asyncio==0.21.1
  pytest-cov==4.1.0
  pytest-mock==3.12.0
  pytest-httpx==0.26.0
  pytest-timeout==2.2.0
  factory-boy==3.3.0
  freezegun==1.4.0
  faker==22.0.0

  # Install
  ./venv/bin/pip install -r requirements.txt
  ```

- [ ] **Update pytest.ini Configuration**
  ```ini
  [pytest]
  # Test discovery
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*

  # Test output
  addopts =
      -v
      --strict-markers
      --tb=short
      --cov=el_pipeline
      --cov=agents
      --cov-report=html
      --cov-report=term-missing
      --cov-fail-under=90
      --asyncio-mode=auto

  # Markers
  markers =
      unit: Unit tests (fast, no external dependencies)
      integration: Integration tests (require databases)
      e2e: End-to-end tests (full stack)
      slow: Slow-running tests

  # Timeout
  timeout = 300

  # Coverage
  [coverage:run]
  source = el_pipeline,agents
  omit =
      */tests/*
      */venv/*
      */__pycache__/*
      */migrations/*

  [coverage:report]
  precision = 2
  show_missing = True
  skip_covered = False
  ```

- [ ] **Create Test Environment File**
  ```bash
  # Create .env.test
  cat > .env.test << 'EOF'
  # Test environment configuration
  OPENAI_API_KEY=test-key-mock
  CUBEJS_API_URL=http://localhost:4000/cubejs-api/v1
  CUBEJS_API_SECRET=test-secret

  # Test databases (will use test containers)
  REFILLS_HOST=localhost
  REFILLS_PORT=5432
  REFILLS_DB=refills_test
  REFILLS_USER=test_user
  REFILLS_PASSWORD=test_pass

  WAREHOUSE_HOST=localhost
  WAREHOUSE_PORT=5435
  WAREHOUSE_DB=warehouse_test
  WAREHOUSE_USER=test_user
  WAREHOUSE_PASSWORD=test_pass
  EOF
  ```

#### Day 2: Test Structure and Shared Fixtures

- [ ] **Create Test Directory Structure**
  ```bash
  mkdir -p tests/{unit,integration,e2e,performance,fixtures}
  mkdir -p tests/unit/{el_pipeline,agents}
  mkdir -p tests/integration/{agents,database,cubejs}
  mkdir -p tests/e2e/{data_pipeline,agent_flows}

  # Create __init__.py files
  find tests -type d -exec touch {}/__init__.py \;
  ```

- [ ] **Create Shared Test Fixtures** (`tests/conftest.py`)
  ```python
  """Shared pytest fixtures for all tests."""
  import pytest
  from unittest.mock import AsyncMock, MagicMock
  from el_pipeline.config import PipelineConfig, DatabaseConfig

  # Test data factories will be added here

  @pytest.fixture
  def mock_openai_client():
      """Mock OpenAI client for agent tests."""
      client = AsyncMock()
      # Configure mock responses
      return client

  @pytest.fixture
  def mock_cubejs_client():
      """Mock Cube.js client."""
      client = AsyncMock()
      return client

  # More fixtures...
  ```

- [ ] **Create Test Data Factories** (`tests/fixtures/factories.py`)
  ```python
  """Test data factories using factory_boy."""
  import factory
  from datetime import datetime, timezone

  class PressOperationFactory(factory.Factory):
      class Meta:
          model = dict

      id = factory.Sequence(lambda n: n)
      timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
      part_family = factory.Iterator(['Door_Outer_Left', 'Door_Outer_Right', 'Bonnet_Outer'])
      # Add more fields...
  ```

---

## Phase 1: Critical Tests (Week 1, Days 3-7)

### Day 3: EL Pipeline Loader Tests

- [ ] **Create test_loader.py** (`tests/unit/el_pipeline/test_loader.py`)
  ```python
  """Tests for DataLoader module."""
  import pytest
  from el_pipeline.loader import DataLoader
  from el_pipeline.config import DatabaseConfig

  @pytest.mark.unit
  def test_load_refills_success(mock_db, sample_refills_data):
      """Test successful refills data loading."""
      loader = DataLoader(mock_db)
      loader.load_refills(sample_refills_data, truncate=True)
      # Assertions...

  @pytest.mark.unit
  def test_load_refills_empty_data(mock_db):
      """Test loading with empty data list."""
      # Test...

  @pytest.mark.unit
  def test_load_refills_handles_duplicates(mock_db, duplicate_data):
      """Test duplicate key handling."""
      # Test...

  # Add 10+ more test cases
  ```

**Checklist:**
- [ ] Test load_refills() with valid data
- [ ] Test load_bodies() with valid data
- [ ] Test load_springs() with valid data
- [ ] Test truncate functionality
- [ ] Test empty data handling
- [ ] Test batch insert with large datasets
- [ ] Test duplicate key handling
- [ ] Test NULL value handling
- [ ] Test timestamp generation (_airbyte_emitted_at)
- [ ] Test connection error handling
- [ ] Test transaction rollback on error
- [ ] Run tests: `./venv/bin/pytest tests/unit/el_pipeline/test_loader.py -v`

### Day 4-5: Agent Core Logic Tests

- [ ] **Create test_manufacturing_advisor.py** (`tests/unit/agents/test_manufacturing_advisor.py`)

**Checklist:**
- [ ] Test enrich_query() with in-scope manufacturing query
- [ ] Test enrich_query() with out-of-scope query (weather)
- [ ] Test part family extraction
- [ ] Test metric extraction
- [ ] Test dimension extraction
- [ ] Test cube recommendation logic
- [ ] Test context handling from previous messages
- [ ] Test guardrails rejection
- [ ] Test OpenAI API error handling
- [ ] Test JSON parsing errors
- [ ] Run tests: `./venv/bin/pytest tests/unit/agents/test_manufacturing_advisor.py -v`

- [ ] **Create test_analytics_specialist.py** (`tests/unit/agents/test_analytics_specialist.py`)

**Checklist:**
- [ ] Test query translation from enriched request
- [ ] Test metric mapping for PressOperations cube
- [ ] Test metric mapping for PartFamilyPerformance cube
- [ ] Test metric mapping for PressLineUtilization cube
- [ ] Test dimension mapping
- [ ] Test filter application
- [ ] Test Cube.js query execution success
- [ ] Test Cube.js query execution failure
- [ ] Test data processing from Cube.js results
- [ ] Test Spore broadcasting
- [ ] Run tests: `./venv/bin/pytest tests/unit/agents/test_analytics_specialist.py -v`

- [ ] **Create test_cubejs_client.py** (`tests/unit/agents/test_cubejs_client.py`)

**Checklist:**
- [ ] Test execute_query() with valid query
- [ ] Test HTTP 4xx error handling
- [ ] Test HTTP 5xx error handling
- [ ] Test connection timeout
- [ ] Test connection refused
- [ ] Test get_meta() success
- [ ] Test health_check() when healthy
- [ ] Test health_check() when unhealthy
- [ ] Run tests: `./venv/bin/pytest tests/unit/agents/test_cubejs_client.py -v`

### Day 6: Visualization and Quality Tests

- [ ] **Create test_visualization_specialist.py** (`tests/unit/agents/test_visualization_specialist.py`)

**Checklist:**
- [ ] Test chart type selection (bar for categorical)
- [ ] Test chart type selection (line for time series)
- [ ] Test chart type selection (table for detailed data)
- [ ] Test Chart.js data format for bar chart
- [ ] Test Chart.js data format for line chart
- [ ] Test Chart.js data format for table
- [ ] Test empty dataset handling
- [ ] Test color scheme application
- [ ] Run tests: `./venv/bin/pytest tests/unit/agents/test_visualization_specialist.py -v`

- [ ] **Create test_quality_inspector.py** (`tests/unit/agents/test_quality_inspector.py`)

**Checklist:**
- [ ] Test anomaly detection in data
- [ ] Test root cause hypothesis generation
- [ ] Test manufacturing domain knowledge application
- [ ] Test insights formatting
- [ ] Run tests: `./venv/bin/pytest tests/unit/agents/test_quality_inspector.py -v`

### Day 7: Report Writer and Basic E2E

- [ ] **Create test_report_writer.py** (`tests/unit/agents/test_report_writer.py`)

**Checklist:**
- [ ] Test narrative composition from data
- [ ] Test actionable recommendations generation
- [ ] Test follow-up questions generation
- [ ] Test final response assembly
- [ ] Test response storage in _pending_responses
- [ ] Run tests: `./venv/bin/pytest tests/unit/agents/test_report_writer.py -v`

- [ ] **Create test_basic_smoke.py** (`tests/e2e/test_basic_smoke.py`)

**Checklist:**
- [ ] Test simple user query flow (mocked)
- [ ] Test agent coordination (mocked)
- [ ] Test response format validation
- [ ] Run tests: `./venv/bin/pytest tests/e2e/test_basic_smoke.py -v`

### Week 1 Exit Criteria

- [ ] All unit tests pass
- [ ] Coverage >= 60%
- [ ] Zero failing tests in CI
- [ ] Test execution time < 2 minutes

**Verification:**
```bash
./venv/bin/pytest tests/unit -v --cov --cov-report=term-missing
```

---

## Phase 2: Integration Tests (Week 2, Days 8-14)

### Day 8-9: Multi-Agent Integration

- [ ] **Create test_agent_collaboration.py** (`tests/integration/agents/test_agent_collaboration.py`)

**Checklist:**
- [ ] Test full Spore message flow (user_query → final_response)
- [ ] Test Manufacturing Advisor → Analytics Specialist flow
- [ ] Test Analytics Specialist → Viz + Quality parallel flow
- [ ] Test Viz + Quality → Report Writer flow
- [ ] Test session_id correlation across agents
- [ ] Test agent failure handling (one agent fails)
- [ ] Test timeout handling (30s limit)
- [ ] Test Spore message ordering
- [ ] Run tests: `./venv/bin/pytest tests/integration/agents/ -v`

### Day 10: dbt Business Logic Tests

- [ ] **Create custom dbt tests** (`dbt_transform/tests/`)

**Files to create:**
- [ ] `assert_oee_calculation_accurate.sql`
- [ ] `assert_pass_rate_matches_raw_data.sql`
- [ ] `assert_cost_calculations_correct.sql`
- [ ] `assert_no_orphaned_records.sql`
- [ ] `assert_grain_press_operations.sql`

**Checklist:**
- [ ] Test OEE = Availability × Performance × Quality
- [ ] Test pass_rate = passed_count / total_count
- [ ] Test total_cost = material + labor + energy
- [ ] Test fact table grain (one row per part)
- [ ] Test referential integrity (FK relationships)
- [ ] Run tests: `docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform`

### Day 11: Cube.js Schema Validation

- [ ] **Create test_cubejs_schemas.py** (`tests/integration/cubejs/test_cubejs_schemas.py`)

**Checklist:**
- [ ] Test PressOperations cube query
- [ ] Test PartFamilyPerformance cube query
- [ ] Test PressLineUtilization cube query
- [ ] Test measure calculations match expected results
- [ ] Test filter application works correctly
- [ ] Test time dimension queries
- [ ] Test joins between cubes
- [ ] Run tests: `./venv/bin/pytest tests/integration/cubejs/ -v`

### Day 12-13: Database Integration Tests

- [ ] **Enhance existing database tests**
- [ ] **Add connection pool tests**
- [ ] **Add transaction tests**
- [ ] **Add error recovery tests**

### Day 14: CLI and Airflow Tests

- [ ] **Create test_cli.py** (`tests/unit/el_pipeline/test_cli.py`)

**Checklist:**
- [ ] Test 'sync' command execution
- [ ] Test 'check' command execution
- [ ] Test argument parsing
- [ ] Test error output formatting
- [ ] Run tests: `./venv/bin/pytest tests/unit/el_pipeline/test_cli.py -v`

- [ ] **Create test_dags.py** (`tests/unit/airflow/test_dags.py`)

**Checklist:**
- [ ] Test DAG imports successfully
- [ ] Test task dependencies are correct
- [ ] Test schedule interval is set
- [ ] Test default args are configured
- [ ] Run tests: `./venv/bin/pytest tests/unit/airflow/ -v`

### Week 2 Exit Criteria

- [ ] All unit + integration tests pass
- [ ] Coverage >= 70%
- [ ] Integration tests complete in < 5 minutes
- [ ] All dbt tests pass

**Verification:**
```bash
./venv/bin/pytest tests/ -v --cov --cov-report=html
```

---

## Phase 3: CI/CD and Pre-Deployment Tests (Week 3)

### Pre-Deployment Test Script

- [ ] **Create scripts/run_tests.sh**
  ```bash
  #!/bin/bash
  set -e

  echo "========================================="
  echo "Running Test Suite Before Deployment"
  echo "========================================="

  # Activate virtual environment
  source ./venv/bin/activate

  # Run unit tests
  echo "→ Running unit tests..."
  pytest tests/unit -v --tb=short --timeout=60 || exit 1

  # Run integration tests (requires test containers)
  echo "→ Running integration tests..."
  pytest tests/integration -v --tb=short --timeout=120 || exit 1

  # Check coverage threshold
  echo "→ Checking coverage threshold (80%)..."
  pytest tests/unit tests/integration --cov --cov-fail-under=90 --cov-report=term-missing || exit 1

  # Run dbt tests (if dbt is available)
  if [ -d "dbt_transform" ]; then
      echo "→ Running dbt tests..."
      dbt test --project-dir=dbt_transform || exit 1
  fi

  echo "========================================="
  echo "✓ All tests passed! Safe to deploy."
  echo "========================================="
  ```

- [ ] **Make script executable**
  ```bash
  chmod +x scripts/run_tests.sh
  ```

### Local Development Workflow

- [ ] **Create scripts/dev_start.sh**
  ```bash
  #!/bin/bash
  set -e

  echo "Starting development environment..."

  # Run tests first
  echo "→ Running pre-deployment tests..."
  ./scripts/run_tests.sh

  # If tests pass, start containers
  echo "→ Tests passed! Starting Docker containers..."
  docker-compose up -d

  # Wait for services to be healthy
  echo "→ Waiting for services to be ready..."
  sleep 10

  # Run E2E smoke tests
  echo "→ Running E2E smoke tests..."
  pytest tests/e2e/test_basic_smoke.py -v || {
      echo "⚠ E2E tests failed. Check logs:"
      echo "  docker logs analytics-agents"
      exit 1
  }

  echo "✓ Development environment ready!"
  echo "  Frontend: http://localhost:3000"
  echo "  Agents API: http://localhost:8000/docs"
  echo "  Cube.js: http://localhost:4000"
  ```

- [ ] **Make script executable**
  ```bash
  chmod +x scripts/dev_start.sh
  ```

### GitHub Actions CI/CD Pipeline

- [ ] **Create .github/workflows/test.yml**
  ```yaml
  name: Test Suite

  on:
    push:
      branches: [main, develop]
    pull_request:
      branches: [main, develop]

  jobs:
    unit-tests:
      name: Unit Tests
      runs-on: ubuntu-latest

      steps:
        - uses: actions/checkout@v3

        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'

        - name: Cache dependencies
          uses: actions/cache@v3
          with:
            path: ~/.cache/pip
            key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}

        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt

        - name: Run unit tests
          run: |
            pytest tests/unit -v --tb=short --cov --cov-report=xml --cov-report=term-missing

        - name: Upload coverage
          uses: codecov/codecov-action@v3
          with:
            file: ./coverage.xml
            fail_ci_if_error: true

    integration-tests:
      name: Integration Tests
      runs-on: ubuntu-latest
      needs: unit-tests

      services:
        postgres:
          image: postgres:15
          env:
            POSTGRES_PASSWORD: test_pass
          options: >-
            --health-cmd pg_isready
            --health-interval 10s
            --health-timeout 5s
            --health-retries 5
          ports:
            - 5432:5432

      steps:
        - uses: actions/checkout@v3

        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'

        - name: Install dependencies
          run: |
            pip install -r requirements.txt

        - name: Run integration tests
          env:
            DATABASE_URL: postgresql://postgres:test_pass@localhost:5432/test_db
          run: |
            pytest tests/integration -v --tb=short

    dbt-tests:
      name: dbt Tests
      runs-on: ubuntu-latest
      needs: integration-tests

      steps:
        - uses: actions/checkout@v3

        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'

        - name: Install dbt
          run: |
            pip install dbt-postgres==1.7.0

        - name: Run dbt tests
          run: |
            cd dbt_transform
            dbt test --profiles-dir=.dbt

    build-and-deploy:
      name: Build and Deploy
      runs-on: ubuntu-latest
      needs: [unit-tests, integration-tests, dbt-tests]
      if: github.ref == 'refs/heads/main'

      steps:
        - uses: actions/checkout@v3

        - name: Build Docker images
          run: |
            docker-compose build

        - name: Start services
          run: |
            docker-compose up -d

        - name: Wait for services
          run: |
            sleep 30

        - name: Run E2E smoke tests
          run: |
            pytest tests/e2e/test_basic_smoke.py -v

        - name: Deploy (if E2E tests pass)
          run: |
            echo "Deployment would happen here"
            # Add actual deployment steps
  ```

### Pre-Commit Hooks

- [ ] **Install pre-commit**
  ```bash
  pip install pre-commit
  ```

- [ ] **Create .pre-commit-config.yaml**
  ```yaml
  repos:
    - repo: local
      hooks:
        - id: pytest-unit
          name: pytest-unit
          entry: bash -c 'source ./venv/bin/activate && pytest tests/unit -v --tb=short -x'
          language: system
          pass_filenames: false
          stages: [commit]

        - id: black
          name: black
          entry: black
          language: system
          types: [python]

        - id: isort
          name: isort
          entry: isort
          language: system
          types: [python]

        - id: flake8
          name: flake8
          entry: flake8
          language: system
          types: [python]
  ```

- [ ] **Install pre-commit hooks**
  ```bash
  pre-commit install
  ```

### Updated docker-compose.yml

- [ ] **Add healthcheck to critical services**
  ```yaml
  services:
    analytics-agents:
      healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
        interval: 10s
        timeout: 5s
        retries: 5
        start_period: 30s
  ```

### Week 3 Exit Criteria

- [ ] CI/CD pipeline fully configured
- [ ] All tests pass in CI before deployment
- [ ] Pre-commit hooks working
- [ ] scripts/dev_start.sh tested and working
- [ ] Coverage >= 75%

---

## Phase 4: Frontend and E2E Tests (Week 4)

### Frontend Testing Setup

- [ ] **Install frontend testing dependencies**
  ```bash
  cd frontend
  npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom
  npm install --save-dev @playwright/test
  ```

- [ ] **Configure Jest** (`frontend/jest.config.js`)
- [ ] **Create component tests** (`frontend/src/components/__tests__/`)
- [ ] **Create E2E tests** (`frontend/e2e/`)

### Full E2E Test Suite

- [ ] **Create test_full_data_pipeline.py** (`tests/e2e/test_full_data_pipeline.py`)

**Checklist:**
- [ ] Test: Source DB → EL → Warehouse
- [ ] Test: Warehouse → dbt → Marts
- [ ] Test: Marts → Cube.js queries
- [ ] Test: Cube.js → Agents → Response
- [ ] Test: Multi-turn conversation
- [ ] Test: Session persistence
- [ ] Test: Error recovery

### Performance Tests

- [ ] **Create test_load.py** (`tests/performance/test_load.py`)

**Checklist:**
- [ ] Test concurrent user load (10 users)
- [ ] Test large query results (>10k rows)
- [ ] Test agent response latency
- [ ] Test database connection pool

### Week 4 Exit Criteria

- [ ] All test suites complete
- [ ] Coverage >= 90%
- [ ] E2E tests pass consistently
- [ ] Performance benchmarks established

---

## Deployment Workflow (Final)

### Production Deployment Process

```bash
# 1. Run full test suite
./scripts/run_tests.sh

# 2. If tests pass, build containers
docker-compose build

# 3. Run E2E tests against built containers
docker-compose up -d
pytest tests/e2e -v

# 4. If E2E tests pass, deploy
# Deploy to production
```

### Makefile for Common Tasks

- [ ] **Create Makefile**
  ```makefile
  .PHONY: test test-unit test-integration test-e2e coverage clean deploy

  test: test-unit test-integration
  	@echo "✓ All tests passed"

  test-unit:
  	./venv/bin/pytest tests/unit -v --tb=short

  test-integration:
  	./venv/bin/pytest tests/integration -v --tb=short

  test-e2e:
  	./venv/bin/pytest tests/e2e -v --tb=short

  coverage:
  	./venv/bin/pytest tests/ --cov --cov-report=html --cov-report=term-missing
  	@echo "Coverage report: htmlcov/index.html"

  clean:
  	find . -type d -name __pycache__ -exec rm -rf {} +
  	find . -type f -name "*.pyc" -delete
  	rm -rf htmlcov .coverage .pytest_cache

  deploy: test
  	@echo "Tests passed! Starting deployment..."
  	./scripts/dev_start.sh
  ```

### Testing Commands Reference

```bash
# Run all tests
make test

# Run specific test suite
make test-unit
make test-integration
make test-e2e

# Generate coverage report
make coverage

# Run tests with specific marker
pytest -m unit
pytest -m integration
pytest -m e2e

# Run tests in parallel (faster)
pytest -n auto

# Run specific test file
pytest tests/unit/agents/test_manufacturing_advisor.py -v

# Run specific test function
pytest tests/unit/agents/test_manufacturing_advisor.py::test_enrich_query_success -v

# Watch mode (run tests on file change)
pytest-watch

# Start development (with pre-deployment tests)
./scripts/dev_start.sh

# Manual deployment workflow
./scripts/run_tests.sh && docker-compose up -d && pytest tests/e2e -v
```

---

## Master Checklist: Test Implementation Progress

### Phase 0: Infrastructure ✓
- [ ] Install all testing dependencies
- [ ] Configure pytest.ini with coverage thresholds
- [ ] Create .env.test file
- [ ] Set up test directory structure
- [ ] Create shared fixtures (conftest.py)
- [ ] Create test data factories

### Phase 1: Critical Unit Tests (Week 1)
- [ ] test_loader.py (11 tests)
- [ ] test_manufacturing_advisor.py (10 tests)
- [ ] test_analytics_specialist.py (10 tests)
- [ ] test_cubejs_client.py (8 tests)
- [ ] test_visualization_specialist.py (8 tests)
- [ ] test_quality_inspector.py (4 tests)
- [ ] test_report_writer.py (5 tests)
- [ ] test_basic_smoke.py (4 tests)
- [ ] **Total: ~60 new tests**
- [ ] Achieve 60% coverage

### Phase 2: Integration Tests (Week 2)
- [ ] test_agent_collaboration.py (8 tests)
- [ ] dbt custom tests (5 SQL tests)
- [ ] test_cubejs_schemas.py (7 tests)
- [ ] test_cli.py (4 tests)
- [ ] test_dags.py (4 tests)
- [ ] **Total: ~28 new tests**
- [ ] Achieve 70% coverage

### Phase 3: CI/CD and Deployment (Week 3)
- [ ] Create scripts/run_tests.sh
- [ ] Create scripts/dev_start.sh
- [ ] Set up GitHub Actions workflow
- [ ] Configure pre-commit hooks
- [ ] Update docker-compose.yml with healthchecks
- [ ] Create Makefile
- [ ] Test full deployment workflow
- [ ] Achieve 75% coverage

### Phase 4: Frontend and E2E (Week 4)
- [ ] Frontend: Jest configuration
- [ ] Frontend: Component tests (10+ tests)
- [ ] Frontend: E2E tests with Playwright (5+ tests)
- [ ] test_full_data_pipeline.py (7 tests)
- [ ] test_load.py (4 performance tests)
- [ ] **Total: ~26 new tests**
- [ ] Achieve 90%+ coverage

### Final Deliverables
- [ ] All 114+ tests passing
- [ ] Coverage >= 90%
- [ ] CI/CD pipeline operational
- [ ] Pre-deployment test script working
- [ ] Documentation updated
- [ ] Team trained on testing workflow

---

## Success Metrics

### Quantitative Metrics
- **Test Count:** 19 → 114+ tests (600% increase)
- **Code Coverage:** 25% → 90%+ (320% increase)
- **Test Execution Time:** < 10 minutes total
- **CI/CD Reliability:** 0% → 95%+ (all tests in CI)

### Qualitative Metrics
- **Deployment Confidence:** Tests pass before any deployment
- **Bug Detection:** Catch issues before production
- **Development Velocity:** Faster iteration with test safety net
- **Code Quality:** Higher quality through test-driven practices

---

## Conclusion

The Praval Manufacturing Analytics System currently has **~25% test coverage** with significant gaps in agent logic, Cube.js, frontend, and end-to-end flows. The EL pipeline has the best coverage at ~70%, while critical components like the multi-agent system have minimal or no tests.

**Critical Actions Required:**
1. **Immediate:** Add unit tests for all agent modules (Priority 1A)
2. **Immediate:** Add loader tests for data pipeline (Priority 1B)
3. **Short-term:** Create basic E2E smoke tests (Priority 1C)
4. **Medium-term:** Build integration test suite for agent collaboration
5. **Long-term:** Establish comprehensive E2E and performance testing

Following the 8-week roadmap will bring the system to **90%+ coverage** and significantly reduce the risk of production issues. The investment in testing infrastructure will pay dividends in system reliability, maintainability, and confidence in future changes.

---

**Report compiled by:** Claude Code
**Analysis scope:** Complete codebase review across 6 major components
**Test files reviewed:** 9
**Source files analyzed:** 50+
**Recommendations:** 60+ specific test scenarios identified
