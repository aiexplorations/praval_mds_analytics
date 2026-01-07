# Data Architecture

End-to-end architecture for the Praval Manufacturing Analytics System, covering data flow from source databases through AI agents to the frontend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SOURCE DATABASES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Press Line A    │  │ Press Line B    │  │ Die Management              │  │
│  │ (PostgreSQL)    │  │ (PostgreSQL)    │  │ (PostgreSQL)                │  │
│  │ Port: 5436      │  │ Port: 5437      │  │ Port: 5438                  │  │
│  │                 │  │                 │  │                             │  │
│  │ Door Panels     │  │ Bonnet Panels   │  │ Die Master, Changeovers,   │  │
│  │ 800T Press      │  │ 1200T Press     │  │ Condition Assessments       │  │
│  │ 2,160 records   │  │ 2,160 records   │  │ 4 dies + events             │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────────┬──────────────┘  │
└───────────┼────────────────────┼───────────────────────────┼────────────────┘
            │                    │                           │
            └────────────────────┼───────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    DATA WAREHOUSE       │
                    │    (PostgreSQL)         │
                    │    Port: 5435           │
                    │                         │
                    │  Foreign Data Wrappers  │
                    │  connect to source DBs  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    dbt TRANSFORMATIONS  │
                    │                         │
                    │  Staging → Intermediate │
                    │      → Marts            │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    CUBE.JS              │
                    │    Semantic Layer       │
                    │    Port: 4000           │
                    │                         │
                    │  3 Cubes with           │
                    │  pre-aggregations       │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    PRAVAL AGENTS        │
                    │    (FastAPI)            │
                    │    Port: 8000           │
                    │                         │
                    │  5 AI Agents            │
                    │  Reef/Spore messaging   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    FRONTEND             │
                    │    (Next.js)            │
                    │    Port: 3000           │
                    │                         │
                    │  Chat Interface         │
                    │  Chart Visualization    │
                    └─────────────────────────┘
```

## 1. Source Databases

Three PostgreSQL databases simulate production systems in an automotive press shop:

### Press Line A (Door Panels)
- **Container**: `postgres-press-line-a`
- **Port**: 5436
- **Database**: `press_line_a`
- **Table**: `press_line_a_production`
- **Data**: 2,160 hourly records (90 days × 24 hours)
- **Press**: 800T capacity
- **Parts**: Door_Outer_Left, Door_Outer_Right

**Key columns**:
- `part_id`, `part_family`, `press_line_id`
- `oee`, `availability`, `performance`, `quality_rate`
- `cycle_time_seconds`, `tonnage_peak`, `stroke_rate_spm`
- `defect_type`, `defect_severity`, `quality_status`
- `material_cost_per_unit`, `labor_cost_per_unit`, `energy_cost_per_unit`

### Press Line B (Bonnet Panels)
- **Container**: `postgres-press-line-b`
- **Port**: 5437
- **Database**: `press_line_b`
- **Table**: `press_line_b_production`
- **Data**: 2,160 hourly records (90 days × 24 hours)
- **Press**: 1200T capacity
- **Parts**: Bonnet_Outer

### Die Management
- **Container**: `postgres-die-management`
- **Port**: 5438
- **Database**: `die_management`
- **Tables**:
  - `die_master`: 4 dies (DIE_DOL_Rev3, DIE_DOR_Rev2, DIE_BO_Rev4, DIE_BO_Rev3)
  - `die_changeover_events`: ~270 changeover records
  - `die_condition_assessments`: ~360 condition assessments

### Data Generation
Data is generated via SQL scripts in `docker/postgres/*/init.sql` using `generate_series()`:
- Realistic hourly production patterns
- Shift variations (day/night/weekend)
- Injected anomalies (die calibration issues, material lot problems)
- Regenerated fresh on `docker-compose down -v && docker-compose up -d`

---

## 2. Data Warehouse

Central PostgreSQL database that consolidates data from all sources.

- **Container**: `postgres-warehouse`
- **Port**: 5435
- **Database**: `warehouse`

### Foreign Data Wrappers
The warehouse uses PostgreSQL FDW to access source databases without data duplication:
```sql
CREATE SERVER press_line_a_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'postgres-press-line-a', port '5432', dbname 'press_line_a');
```

### Schemas
| Schema | Purpose |
|--------|---------|
| `raw` | Legacy pen manufacturing tables (deprecated) |
| `staging` | dbt staging models |
| `marts` | dbt mart models |
| `staging_marts` | dbt automotive mart models |

---

## 3. dbt Transformations

dbt transforms raw data into analytics-ready models.

### Model Layers

```
Source (FDW) → Staging → Intermediate → Marts
```

### Staging Models (4)
Clean and standardize raw data:
- `stg_press_line_a_production.sql`
- `stg_press_line_b_production.sql`
- `stg_die_management.sql`
- `stg_material_coils.sql`

### Intermediate Models (2+)
Apply business logic:
- `int_automotive_production_combined.sql` - Union of both press lines
- `int_daily_production_by_press.sql` - Daily aggregations

### Mart Models (7+)
Analytics-ready dimensional models:
- `fact_press_operations.sql` - Production-level fact table
- `agg_part_family_performance.sql` - Aggregated by part family
- `agg_press_line_utilization.sql` - Aggregated by press line
- `fact_defect_analysis.sql` - Defect-focused analysis
- `agg_machine_performance.sql` - Machine metrics

### Running dbt
```bash
# Inside Docker container
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform
docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform
```

---

## 4. Cube.js Semantic Layer

Cube.js provides a semantic layer with pre-defined measures, dimensions, and pre-aggregations.

- **Container**: `cubejs`
- **Port**: 4000
- **Playground**: http://localhost:4000

### Cubes (3)

| Cube | Source Table | Purpose |
|------|--------------|---------|
| `PressOperations` | `staging_marts.fact_press_operations` | Production-level data with full traceability |
| `PartFamilyPerformance` | `staging_marts.agg_part_family_performance` | Aggregated by part family |
| `PressLineUtilization` | `staging_marts.agg_press_line_utilization` | Line capacity and utilization |

### PressOperations Cube
**Measures**:
- `count`, `passedCount`, `failedCount`, `passRate`
- `avgOee`, `avgAvailability`, `avgPerformance`, `avgQualityRate`
- `avgTonnage`, `avgCycleTime`, `avgStrokeRate`
- `totalCost`, `avgCostPerPart`, `defectCount`, `reworkCount`

**Dimensions**:
- `partFamily`, `pressLineId`, `lineName`, `dieId`
- `shiftId`, `operatorId`, `materialGrade`, `coilId`
- `defectType`, `defectSeverity`, `qualityStatus`
- `productionDate`, `isWeekend`

**Pre-aggregations**:
- `main`: Daily aggregation by partFamily, pressLineId, partType
- `byShift`: Daily aggregation by partFamily, shiftId

---

## 5. Airflow Orchestration

Apache Airflow orchestrates the data pipeline.

- **Container**: `airflow-webserver`
- **Port**: 8080
- **Credentials**: admin/admin

### DAG: mds_pipeline

Runs daily at midnight:

```
run_el_pipeline → run_dbt_transformations → run_dbt_tests → generate_summary
```

| Task | Description |
|------|-------------|
| `run_el_pipeline` | Extract-Load from source DBs to warehouse |
| `run_dbt_transformations` | Run all dbt models |
| `run_dbt_tests` | Validate data quality |
| `generate_summary` | Log completion summary |

---

## 6. Praval AI Agents

Five specialized AI agents communicate via Praval's event-driven Reef/Spore architecture.

- **Container**: `analytics-agents`
- **Port**: 8000
- **API Docs**: http://localhost:8000/docs

### Agent Communication Flow

```
User Query (HTTP POST /chat)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI broadcasts Spore: user_query                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Manufacturing Advisor                                        │
│ • Enriches query with domain knowledge                      │
│ • Maps terminology ("doors" → Door_Outer_Left/Right)        │
│ • Broadcasts: domain_enriched_request                       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Analytics Specialist                                         │
│ • Translates to Cube.js query                               │
│ • Executes via HTTP to Cube.js container                    │
│ • Broadcasts: data_ready                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ├───────────────────────────────────────┐
    ▼                                       ▼
┌─────────────────────────┐   ┌─────────────────────────────────┐
│ Visualization Specialist │   │ Quality Inspector               │
│ • Selects chart type     │   │ • Detects anomalies             │
│ • Generates Chart.js     │   │ • Generates root cause analysis │
│ • Broadcasts: chart_ready│   │ • Broadcasts: insights_ready    │
└─────────────────────────┘   └─────────────────────────────────┘
    │                                       │
    └───────────────────┬───────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ Report Writer                                                │
│ • Waits for BOTH chart_ready AND insights_ready             │
│ • Composes narrative with LLM                               │
│ • Generates follow-up suggestions                           │
│ • Broadcasts: final_response_ready                          │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI returns ChatResponse to frontend                     │
└─────────────────────────────────────────────────────────────┘
```

### Agent Details

| Agent | Responds To | Broadcasts | Purpose |
|-------|-------------|------------|---------|
| Manufacturing Advisor | `user_query` | `domain_enriched_request` | Domain expertise, terminology mapping |
| Analytics Specialist | `domain_enriched_request` | `data_ready` | Query translation, Cube.js execution |
| Visualization Specialist | `data_ready` | `chart_ready` | Chart type selection, Chart.js specs |
| Quality Inspector | `data_ready` | `insights_ready` | Anomaly detection, root cause analysis |
| Report Writer | `chart_ready`, `insights_ready` | `final_response_ready` | Narrative composition |

### Key Design Decisions

1. **No Orchestrator**: Agents self-coordinate via pub/sub messaging
2. **Parallel Execution**: Visualization and Quality agents run simultaneously
3. **Session Correlation**: Report Writer uses `session_id` to match chart + insights
4. **Graceful Degradation**: System works even if one agent fails
5. **LLM Integration**: Each agent uses GPT-4o-mini for its specific task

---

## 7. Frontend

Next.js chat interface with real-time visualization.

- **Container**: `analytics-frontend`
- **Port**: 3000
- **URL**: http://localhost:3000

### Features
- Natural language chat interface
- Dynamic Chart.js visualizations (bar, line, table)
- Suggested follow-up questions
- Session-based conversation history

### API Integration
```typescript
POST /chat
{
  "message": "What's the OEE by press line?",
  "session_id": "optional-session-id"
}

Response:
{
  "message": "Line A has 85.8% OEE vs Line B at 79.1%...",
  "session_id": "abc123",
  "chart": { /* Chart.js specification */ },
  "insights": ["Line A outperforms Line B..."],
  "suggested_questions": ["Compare by shift", "Show trends"]
}
```

---

## Data Flow Summary

| Step | Component | Action |
|------|-----------|--------|
| 1 | Source DBs | Generate production data via init.sql |
| 2 | Warehouse | Access source data via Foreign Data Wrappers |
| 3 | dbt | Transform: staging → intermediate → marts |
| 4 | Cube.js | Serve pre-aggregated metrics via REST API |
| 5 | Praval Agents | Process user queries through 5-agent pipeline |
| 6 | Frontend | Display results with charts and insights |
| 7 | Airflow | Orchestrate daily pipeline refresh |

---

## Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service definitions and networking |
| `.env` / `.env.example` | Environment variables (API keys) |
| `dbt_transform/dbt_project.yml` | dbt project configuration |
| `.dbt/profiles.yml` | dbt database connection |
| `cubejs/.env` | Cube.js database connection |
| `agents/config.py` | Agent configuration (model, endpoints) |

---

## Related Documentation

- [Agent Architecture](AGENT_ARCHITECTURE.md) - Detailed Praval agent implementation
- [Automotive Dataset](AUTOMOTIVE_DATASET.md) - Dataset specification and use cases
- [README](../README.md) - Quick start guide and overview
