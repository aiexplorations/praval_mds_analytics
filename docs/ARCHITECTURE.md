# Praval Manufacturing Analytics System - Architecture

## System Overview

AI-powered analytics platform for automotive press manufacturing using multi-agent intelligence (Praval framework). Tracks production metrics for 2 press lines (800T and 1200T) producing door and bonnet panels with real-time analytics, anomaly detection, and natural language querying.

**Technology Stack:**
- **Agents:** Praval 0.7.16 (multi-agent framework)
- **Backend:** FastAPI, Python 3.11
- **Frontend:** Next.js 14, React, TypeScript
- **Data:** PostgreSQL 15, dbt 1.7
- **Analytics:** Cube.js (semantic layer)
- **Orchestration:** Apache Airflow 2.7.3
- **LLM:** OpenAI GPT-4o-mini

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │  Next.js 14 Frontend (Port 3000)                               │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
    │  │ Chat         │  │ Agent List   │  │ Chart        │         │
    │  │ Interface    │  │ Sidebar      │  │ Visualization│         │
    │  └──────────────┘  └──────────────┘  └──────────────┘         │
    └────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-AGENT BACKEND LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │  FastAPI Application (Port 8000)                                │
    │  ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
    │  │ /chat       │ /agents     │ /health     │ /session/*  │     │
    │  │ endpoint    │ endpoint    │ endpoint    │ endpoints   │     │
    │  └─────────────┴─────────────┴─────────────┴─────────────┘     │
    │                                                                  │
    │  ┌──────────────────────────────────────────────────────┐      │
    │  │  Session Manager (In-Memory)                         │      │
    │  │  - Conversation history tracking                     │      │
    │  │  - Context management (5-message window)             │      │
    │  └──────────────────────────────────────────────────────┘      │
    └────────────────────────┬─────────────────────────────────────────┘
                             │ Broadcasts user_query Spores
                             ▼
    ┌──────────────────────────────────────────────────────────────────┐
    │  Praval Reef (In-Memory Message Queue / Event Bus)              │
    │  ┌────────────────────────────────────────────────────────────┐ │
    │  │  Channel: "main"                                           │ │
    │  │  - Event-driven pub/sub messaging                          │ │
    │  │  - Spores (JSON messages) with typed knowledge            │ │
    │  │  - Async agent communication                               │ │
    │  └────────────────────────────────────────────────────────────┘ │
    └────────┬─────────┬─────────┬─────────┬─────────┬──────────┬─────┘
             │         │         │         │         │          │
    ┌────────▼─────┐ ┌▼────────┐┌▼────────┐┌▼────────┐┌▼────────┐┌▼────────┐
    │Manufacturing │ │Analytics││Visualiza││Quality  ││Report   ││Response │
    │Advisor       │ │Special- ││tion     ││Inspector││Writer   ││Storage  │
    │Agent         │ │ist      ││Special- ││Agent    ││Agent    ││Agent    │
    │              │ │Agent    ││ist      ││         ││         ││         │
    │@agent        │ │@agent   ││@agent   ││@agent   ││@agent   ││@agent   │
    ├──────────────┤ ├─────────┤├─────────┤├─────────┤├─────────┤├─────────┤
    │Responds to:  │ │Responds ││Responds ││Responds ││Responds ││Responds │
    │• user_query  │ │to:      ││to:      ││to:      ││to:      ││to:      │
    │              │ │• domain_││• data_  ││• data_  ││• all    ││• final_ │
    │Broadcasts:   │ │  enriched│  ready  ││  ready  ││  prior  ││  response│
    │• domain_     │ │  request││         ││         ││  spores ││  ready  │
    │  enriched_   │ │         ││Broad-   ││Broad-   ││         ││         │
    │  request     │ │Broad-   ││casts:   ││casts:   ││Broad-   ││Stores   │
    │              │ │casts:   ││• chart_ ││• anomaly││casts:   ││response │
    │Domain        │ │• data_  ││  spec   ││  alerts ││• final_ ││in HTTP  │
    │expertise &   │ │  ready  ││         ││         ││  response│endpoint │
    │terminology   │ │         ││Chart    ││Root     ││  ready  ││         │
    │mapping       │ │Query    ││type     ││cause    ││         ││Composes │
    │              │ │execution││selection││analysis ││Narrative││narrative│
    └──────────────┘ └────┬────┘└─────────┘└─────────┘└─────────┘└─────────┘
                          │
                          │ Queries Cube.js
                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         SEMANTIC/METRICS LAYER                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │  Cube.js Server (Port 4000)                                     │
    │  ┌────────────────────────────────────────────────────────────┐ │
    │  │  Cubes (Semantic Models):                                  │ │
    │  │  ┌──────────────────┐ ┌──────────────────┐                │ │
    │  │  │ PressOperations  │ │ PartFamily       │                │ │
    │  │  │                  │ │ Performance      │                │ │
    │  │  │ Measures:        │ │                  │                │ │
    │  │  │ • total_parts    │ │ Measures:        │                │ │
    │  │  │ • defect_count   │ │ • avg_oee        │                │ │
    │  │  │ • defect_rate    │ │ • first_pass_    │                │ │
    │  │  │ • avg_cycle_time │ │   yield          │                │ │
    │  │  │ • avg_tonnage    │ │ • total_defects  │                │ │
    │  │  │                  │ │                  │                │ │
    │  │  │ Dimensions:      │ │ Dimensions:      │                │ │
    │  │  │ • part_family    │ │ • part_family    │                │ │
    │  │  │ • defect_type    │ │ • press_line     │                │ │
    │  │  │ • press_line     │ │ • shift          │                │ │
    │  │  │ • shift          │ │ • date           │                │ │
    │  │  │ • production_date│ │                  │                │ │
    │  │  │ • coil_id        │ │                  │                │ │
    │  │  │ • die_id         │ │                  │                │ │
    │  │  └──────────────────┘ └──────────────────┘                │ │
    │  │                                                            │ │
    │  │  ┌──────────────────┐                                     │ │
    │  │  │ PressLine        │                                     │ │
    │  │  │ Utilization      │                                     │ │
    │  │  │                  │                                     │ │
    │  │  │ Measures:        │                                     │ │
    │  │  │ • utilization_   │                                     │ │
    │  │  │   rate           │                                     │ │
    │  │  │ • downtime_hours │                                     │ │
    │  │  │ • parts_per_hour │                                     │ │
    │  │  │                  │                                     │ │
    │  │  │ Dimensions:      │                                     │ │
    │  │  │ • press_line     │                                     │ │
    │  │  │ • shift          │                                     │ │
    │  │  │ • date           │                                     │ │
    │  │  └──────────────────┘                                     │ │
    │  └────────────────────────────────────────────────────────────┘ │
    └────────────────────────┬───────────────────────────────────────┘
                             │ SQL Queries
                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         DATA TRANSFORMATION LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │  PostgreSQL Data Warehouse (Port 5435)                          │
    │                                                                  │
    │  ┌────────────────────────────────────────────────────────────┐ │
    │  │  dbt Transformations (SQL-based ELT)                       │ │
    │  │                                                            │ │
    │  │  Staging Layer (Raw → Clean):                             │ │
    │  │  ┌─────────────────────────────────────────────────────┐  │ │
    │  │  │ • stg_press_line_a_production                       │  │ │
    │  │  │ • stg_press_line_b_production                       │  │ │
    │  │  │ • stg_die_management                                │  │ │
    │  │  │ • stg_material_coils                                │  │ │
    │  │  │                                                     │  │ │
    │  │  │ Transformations:                                    │  │ │
    │  │  │ - Type casting, date parsing                        │  │ │
    │  │  │ - NULL handling, deduplication                      │  │ │
    │  │  │ - Column renaming for consistency                   │  │ │
    │  │  └─────────────────────────────────────────────────────┘  │ │
    │  │                                                            │ │
    │  │  Intermediate Layer (Business Logic):                     │ │
    │  │  ┌─────────────────────────────────────────────────────┐  │ │
    │  │  │ • int_automotive_production_combined                │  │ │
    │  │  │   (Union of Line A + Line B)                        │  │ │
    │  │  │ • int_daily_production_by_press                     │  │ │
    │  │  │ • int_production_quality                            │  │ │
    │  │  │                                                     │  │ │
    │  │  │ Transformations:                                    │  │ │
    │  │  │ - OEE calculations                                  │  │ │
    │  │  │ - Defect rate computations                          │  │ │
    │  │  │ - Material traceability joins                       │  │ │
    │  │  │ - Die changeover (SMED) metrics                     │  │ │
    │  │  └─────────────────────────────────────────────────────┘  │ │
    │  │                                                            │ │
    │  │  Marts Layer (Analytics-Ready):                           │ │
    │  │  ┌─────────────────────────────────────────────────────┐  │ │
    │  │  │ • fact_press_operations                             │  │ │
    │  │  │   (Hourly production detail)                        │  │ │
    │  │  │ • fact_hourly_production_detail                     │  │ │
    │  │  │ • fact_production_quality                           │  │ │
    │  │  │ • fact_defect_analysis                              │  │ │
    │  │  │ • agg_part_family_performance                       │  │ │
    │  │  │ • agg_press_line_utilization                        │  │ │
    │  │  │ • agg_material_performance                          │  │ │
    │  │  │ • agg_machine_performance                           │  │ │
    │  │  │ • agg_component_quality_trends                      │  │ │
    │  │  │                                                     │  │ │
    │  │  │ Optimized for Cube.js consumption                   │  │ │
    │  │  └─────────────────────────────────────────────────────┘  │ │
    │  └────────────────────────────────────────────────────────────┘ │
    │                                                                  │
    │  Foreign Data Wrappers (postgres_fdw):                          │
    │  ┌────────────────────────────────────────────────────────────┐ │
    │  │ • fdw_press_line_a   → postgres-press-line-a:5432         │ │
    │  │ • fdw_press_line_b   → postgres-press-line-b:5432         │ │
    │  │ • fdw_die_management → postgres-die-management:5432       │ │
    │  └────────────────────────────────────────────────────────────┘ │
    └────────────────────────┬───────────────────────────────────────┘
                             │ FDW Queries
                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SOURCE DATA LAYER                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────┐  ┌────────────────────────┐  ┌──────────────────┐
    │ PostgreSQL DB         │  │ PostgreSQL DB          │  │ PostgreSQL DB    │
    │ Press Line A          │  │ Press Line B           │  │ Die Management   │
    │ (Port 5436)           │  │ (Port 5437)            │  │ (Port 5438)      │
    ├───────────────────────┤  ├────────────────────────┤  ├──────────────────┤
    │ Tables:               │  │ Tables:                │  │ Tables:          │
    │ • production_records  │  │ • production_records   │  │ • die_inventory  │
    │ • defects             │  │ • defects              │  │ • die_changes    │
    │ • material_coils      │  │ • material_coils       │  │ • die_           │
    │                       │  │                        │  │   maintenance    │
    │ Press: 800T           │  │ Press: 1200T           │  │                  │
    │ Parts:                │  │ Parts:                 │  │ 4 Dies:          │
    │ • Door_Outer_Left     │  │ • Bonnet_Outer         │  │ • DIE-001        │
    │ • Door_Outer_Right    │  │                        │  │ • DIE-002        │
    │                       │  │                        │  │ • DIE-003        │
    │ 3 Shifts/Day          │  │ 3 Shifts/Day           │  │ • DIE-004        │
    │ 126 Material Coils    │  │ 126 Material Coils     │  │                  │
    │ 3 Suppliers           │  │ 3 Suppliers            │  │ SMED Tracking    │
    └───────────────────────┘  └────────────────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────┐
    │  Apache Airflow (Port 8080)                                     │
    │  ┌────────────────────────────────────────────────────────────┐ │
    │  │  DAGs:                                                     │ │
    │  │  ┌──────────────────────────────────────────────────────┐ │ │
    │  │  │ EL Pipeline DAG                                      │ │ │
    │  │  │ • Extract from source DBs (via FDW)                  │ │ │
    │  │  │ • Load to warehouse staging tables                   │ │ │
    │  │  │ • Schedule: Hourly / On-demand                       │ │ │
    │  │  └──────────────────────────────────────────────────────┘ │ │
    │  │  ┌──────────────────────────────────────────────────────┐ │ │
    │  │  │ dbt Transformation DAG                               │ │ │
    │  │  │ • Run dbt models (staging → intermediate → marts)    │ │ │
    │  │  │ • Data quality tests                                 │ │ │
    │  │  │ • Schedule: After EL completes                       │ │ │
    │  │  └──────────────────────────────────────────────────────┘ │ │
    │  │                                                            │ │
    │  │  Metadata DB: PostgreSQL airflow-db:5432                  │ │
    │  └────────────────────────────────────────────────────────────┘ │
    └──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE                                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

    Docker Compose (docker-compose.yml)
    ├── Network: mds-network (bridge)
    ├── Volumes:
    │   ├── postgres-press-line-a-data
    │   ├── postgres-press-line-b-data
    │   ├── postgres-die-management-data
    │   ├── postgres-warehouse-data
    │   └── airflow-db-data
    └── Health Checks:
        ├── PostgreSQL databases (pg_isready)
        └── Airflow DB (pg_isready)
```

---

## Data Flow

### 1. Data Ingestion Flow

```
Source DBs → FDW → Warehouse Staging → dbt Transform → Marts → Cube.js → Agents
```

**Detailed Steps:**
1. **Extraction:** Airflow triggers EL pipeline
2. **Loading:** Data copied from source DBs to warehouse via Foreign Data Wrappers
3. **Staging:** dbt runs staging models (type casting, cleaning, deduplication)
4. **Transformation:** dbt runs intermediate models (OEE calc, defect rates, joins)
5. **Marts:** dbt creates analytics-ready fact and aggregate tables
6. **Semantic Layer:** Cube.js exposes marts as queryable cubes with measures/dimensions
7. **Agent Access:** Analytics Specialist agent queries Cube.js via HTTP API

### 2. User Query Flow

```
User Input → Frontend → FastAPI → Reef (Spores) → Agents → Cube.js → Response
```

**Detailed Agent Workflow:**

1. **User sends query** via chat interface (Frontend)
2. **FastAPI /chat endpoint** receives message, creates session, broadcasts `user_query` Spore
3. **Manufacturing Advisor** receives `user_query`:
   - Enriches with domain knowledge (terminology, context)
   - Maps user intent to manufacturing concepts
   - Broadcasts `domain_enriched_request` Spore
4. **Analytics Specialist** receives `domain_enriched_request`:
   - Translates to Cube.js query
   - Executes query via HTTP
   - Broadcasts `data_ready` Spore with results
5. **Visualization Specialist** (parallel) receives `data_ready`:
   - Analyzes data structure
   - Selects chart type (bar/line/table)
   - Broadcasts `chart_spec` Spore
6. **Quality Inspector** (parallel) receives `data_ready`:
   - Runs anomaly detection
   - Performs root cause analysis
   - Broadcasts `anomaly_alerts` Spore (if issues found)
7. **Report Writer** receives all prior Spores:
   - Composes narrative response
   - Integrates chart spec and insights
   - Broadcasts `final_response_ready` Spore
8. **Response Storage** receives `final_response_ready`:
   - Stores in temporary dict keyed by session_id
9. **FastAPI endpoint** polls for response:
   - Returns ChatResponse to frontend
10. **Frontend** displays message, chart, and suggested questions

### 3. Praval Spore Message Flow

```
Spore Structure:
{
  "id": "uuid",
  "type": "user_query | domain_enriched_request | data_ready | chart_spec | ...",
  "knowledge": { /* typed data payload */ },
  "from_agent": "agent_name",
  "timestamp": "ISO-8601"
}
```

**Event-Driven Communication:**
- Agents subscribe via `@agent(responds_to=["message_type"])`
- No orchestrator - agents self-coordinate
- Async, non-blocking message passing
- In-memory pub/sub via Reef

---

## System Components

### 1. Frontend Layer

**Technology:** Next.js 14, React, TypeScript, TailwindCSS

**Components:**
- `ChatInterface`: Main chat UI with message history
- `LeftSidebar`: Dataset info and dynamic agent list (fetched from `/agents` endpoint)
- `Chart`: Visualizations using Chart.js (bar, line, table)
- `Insights Panel`: Bullet points extracted from narrative

**API Client:** Axios-based (`frontend/src/lib/api.ts`)
- `sendMessage()`: POST /chat
- `getAgents()`: GET /agents
- `healthCheck()`: GET /health
- `deleteSession()`: DELETE /session/{id}

### 2. Backend Layer

**Technology:** FastAPI, Uvicorn, Python 3.11

**Core Modules:**
- `app.py`: Main FastAPI application with endpoints
- `session_manager.py`: In-memory session tracking (conversation history)
- `cubejs_client.py`: HTTP client for Cube.js API
- `config.py`: Pydantic settings (OpenAI API key, Cube.js URL, etc.)
- `models.py`: Request/response models (ChatRequest, ChatResponse, AgentInfo, etc.)

**Endpoints:**
- `GET /`: Service info
- `GET /health`: Health check (includes Cube.js connectivity)
- `GET /agents`: List of registered Praval agents
- `POST /chat`: Main chat endpoint (broadcasts user_query, waits for response)
- `GET /session/{id}`: Session info
- `DELETE /session/{id}`: Delete session

### 3. Multi-Agent System (Praval)

**Technology:** Praval 0.7.16, OpenAI GPT-4o-mini

**Agents:**

#### Manufacturing Advisor (`manufacturing_advisor.py`)
- **Role:** Senior manufacturing engineer with 20+ years in automotive stamping
- **Responds to:** `user_query`
- **Broadcasts:** `domain_enriched_request`, `conversational_response`
- **Capabilities:**
  - Manufacturing terminology understanding (OEE, SMED, tonnage, springback)
  - Part family mapping (e.g., "doors" → Door_Outer_Left, Door_Outer_Right)
  - Context tracking (references to "these parts", "that metric")
  - Guardrails (rejects out-of-scope queries)

#### Analytics Specialist (`analytics_specialist.py`)
- **Role:** Data analyst specializing in press shop metrics
- **Responds to:** `domain_enriched_request`
- **Broadcasts:** `data_ready`, `query_execution_error`
- **Capabilities:**
  - Cube.js query translation
  - Schema knowledge (cubes, measures, dimensions)
  - Query optimization (filters, aggregations, groupBy)
  - Error handling and fallback queries

#### Visualization Specialist (`visualization_specialist.py`)
- **Role:** Data visualization expert
- **Responds to:** `data_ready`
- **Broadcasts:** `chart_spec`
- **Capabilities:**
  - Chart type selection (bar for comparisons, line for trends, table for detail)
  - Chart.js config generation
  - Data transformation for visualization
  - Responsive design considerations

#### Quality Inspector (`quality_inspector.py`)
- **Role:** Quality engineer focused on anomaly detection
- **Responds to:** `data_ready`
- **Broadcasts:** `anomaly_alerts`
- **Capabilities:**
  - Statistical anomaly detection (z-score, IQR methods)
  - Root cause analysis (material, die, shift correlation)
  - Threshold-based alerts (defect rate > 5%, OEE < 85%)
  - Pattern recognition in defects

#### Report Writer (`report_writer.py`)
- **Role:** Technical writer composing insights
- **Responds to:** All prior Spores in sequence
- **Broadcasts:** `final_response_ready`
- **Capabilities:**
  - Narrative composition (integrates data, chart, insights)
  - Follow-up question generation
  - Context-aware writing (manufacturing terminology)
  - Markdown formatting

#### Response Storage (`report_writer.py`)
- **Role:** HTTP endpoint integration handler
- **Responds to:** `final_response_ready`
- **Capabilities:**
  - Stores response in temporary dict by session_id
  - Enables FastAPI polling mechanism
  - Cleans up after response retrieved

**Communication Architecture:**
- **Reef:** In-memory message queue (pub/sub)
- **Spores:** Typed JSON messages with knowledge payloads
- **Channels:** Default "main" channel for all agents
- **Registry:** Global agent registry (accessible via `get_registry()`)
- **Network Stats:** Available via `reef.get_network_stats()`

### 4. Semantic Layer

**Technology:** Cube.js (latest), PostgreSQL

**Cubes:**

#### PressOperations (`cubejs/schema/PressOperations.js`)
- **Source:** `fact_press_operations` mart
- **Measures:**
  - `total_parts`: Count of parts produced
  - `defect_count`: Count of defects
  - `defect_rate`: Defects / Total parts
  - `avg_cycle_time`: Average cycle time (seconds)
  - `avg_tonnage`: Average press tonnage
- **Dimensions:**
  - `part_family`: Door_Outer_Left, Door_Outer_Right, Bonnet_Outer
  - `defect_type`: springback, burr, crack, warp, scratch
  - `press_line`: Line A (800T), Line B (1200T)
  - `shift`: Morning, Afternoon, Night
  - `production_date`: Date hierarchy
  - `coil_id`: Material coil identifier
  - `die_id`: Die identifier

#### PartFamilyPerformance (`cubejs/schema/PartFamilyPerformance.js`)
- **Source:** `agg_part_family_performance` mart
- **Measures:**
  - `avg_oee`: Overall Equipment Effectiveness (%)
  - `first_pass_yield`: Good parts on first try (%)
  - `total_defects`: Defect count
  - `production_volume`: Total parts
- **Dimensions:**
  - `part_family`
  - `press_line`
  - `shift`
  - `date`

#### PressLineUtilization (`cubejs/schema/PressLineUtilization.js`)
- **Source:** `agg_press_line_utilization` mart
- **Measures:**
  - `utilization_rate`: Uptime / Available time (%)
  - `downtime_hours`: Hours of downtime
  - `parts_per_hour`: Production rate
- **Dimensions:**
  - `press_line`
  - `shift`
  - `date`

### 5. Data Transformation Layer

**Technology:** dbt 1.7, PostgreSQL, SQL

**Layer Structure:**

#### Staging Models (`dbt_transform/models/staging/`)
- `stg_press_line_a_production`: Clean Line A data
- `stg_press_line_b_production`: Clean Line B data
- `stg_die_management`: Clean die data
- `stg_material_coils`: Clean material data

**Transformations:** Type casting, NULL handling, deduplication, column renaming

#### Intermediate Models (`dbt_transform/models/intermediate/`)
- `int_automotive_production_combined`: Union of Line A + Line B
- `int_daily_production_by_press`: Daily aggregates by press
- `int_production_quality`: OEE calculations, defect rates

**Business Logic:** OEE formulas, material traceability joins, SMED metrics

#### Mart Models (`dbt_transform/models/marts/`)
- `fact_press_operations`: Hourly production detail
- `fact_hourly_production_detail`: Granular production records
- `fact_production_quality`: Quality metrics
- `fact_defect_analysis`: Defect drill-down
- `agg_part_family_performance`: Part family aggregates
- `agg_press_line_utilization`: Press line aggregates
- `agg_material_performance`: Material supplier aggregates
- `agg_machine_performance`: Machine-level metrics
- `agg_component_quality_trends`: Quality over time

### 6. Data Sources

**Technology:** PostgreSQL 15

#### Press Line A Database (Port 5436)
- **Tables:** production_records, defects, material_coils
- **Press:** 800T hydraulic press
- **Parts:** Door_Outer_Left, Door_Outer_Right
- **Shifts:** 3 shifts/day (Morning 6-14, Afternoon 14-22, Night 22-6)
- **Materials:** 126 coils from 3 suppliers (SteelCo, MetalWorks, AlloyCorp)

#### Press Line B Database (Port 5437)
- **Tables:** production_records, defects, material_coils
- **Press:** 1200T hydraulic press
- **Parts:** Bonnet_Outer
- **Shifts:** 3 shifts/day
- **Materials:** 126 coils from 3 suppliers

#### Die Management Database (Port 5438)
- **Tables:** die_inventory, die_changes, die_maintenance
- **Dies:** 4 dies (DIE-001, DIE-002, DIE-003, DIE-004)
- **SMED Tracking:** Die changeover times, maintenance schedules
- **Lifecycle:** Installation date, total shots, condition status

### 7. Data Warehouse

**Technology:** PostgreSQL 15 with postgres_fdw extension

**Foreign Data Wrappers:**
- `fdw_press_line_a` → postgres-press-line-a:5432
- `fdw_press_line_b` → postgres-press-line-b:5432
- `fdw_die_management` → postgres-die-management:5432

**Purpose:**
- Central repository for transformed data
- Hosts dbt models (staging, intermediate, marts)
- Exposes data to Cube.js semantic layer
- Maintains data lineage and versioning

### 8. Orchestration

**Technology:** Apache Airflow 2.7.3, Python 3.11

**DAGs:**

#### EL Pipeline DAG (`airflow/dags/el_pipeline_dag.py`)
- **Schedule:** Hourly or on-demand
- **Tasks:**
  1. Extract data from source DBs via FDW
  2. Load to warehouse staging tables
  3. Data quality checks
- **Monitoring:** Task logs, email alerts on failure

#### dbt Transformation DAG (`airflow/dags/dbt_transform_dag.py`)
- **Schedule:** Triggered after EL completes
- **Tasks:**
  1. Run dbt staging models
  2. Run dbt intermediate models
  3. Run dbt mart models
  4. Run dbt tests (data quality)
- **Monitoring:** Model run times, test failures

**Infrastructure:**
- **Metadata DB:** PostgreSQL airflow-db:5432
- **Executor:** LocalExecutor
- **Web UI:** http://localhost:8080 (admin/admin)

---

## Key Design Decisions

### 1. Event-Driven Multi-Agent System (Praval)

**Rationale:**
- **No central orchestrator** - agents self-coordinate via message passing
- **Parallel execution** - Visualization and Quality agents run simultaneously
- **Graceful degradation** - system works even if individual agents fail
- **Extensibility** - new agents can be added without modifying existing ones

**Trade-offs:**
- Complexity: Async message flow harder to debug than synchronous calls
- Timing: Requires polling mechanism for HTTP response synchronization

### 2. In-Memory Reef (vs. RabbitMQ/Redis)

**Rationale:**
- Low latency (< 1ms message passing)
- Simplified deployment (no external message broker)
- Sufficient for single-server deployment

**Trade-offs:**
- Not horizontally scalable (single process)
- Messages lost on restart (no persistence)
- Future: Could switch to Redis backend for multi-server setup

### 3. Cube.js Semantic Layer

**Rationale:**
- Consistent metrics across all agents
- Caching and query optimization
- Schema versioning and evolution
- REST API for LLM access

**Trade-offs:**
- Additional layer of abstraction
- Learning curve for cube schema DSL

### 4. Foreign Data Wrappers (vs. EL tool)

**Rationale:**
- Zero-ETL for simple queries
- Real-time access to source data
- No additional tooling (built into PostgreSQL)

**Trade-offs:**
- Performance: FDW queries slower than local tables
- Requires source DBs to be online
- Network latency

### 5. dbt for Transformations

**Rationale:**
- SQL-based (accessible to data analysts)
- Version control for transformations
- Built-in testing framework
- Modular, reusable models

**Trade-offs:**
- Requires separate orchestration (Airflow)
- Learning curve for dbt-specific syntax

---

## Scalability Considerations

### Current Limits
- **Single-server deployment** (all services on one machine via Docker Compose)
- **In-memory Reef** (not horizontally scalable)
- **Session storage** (in-memory dict, lost on restart)

### Future Scaling Paths

#### Horizontal Scaling
1. **Multi-agent parallelism:**
   - Deploy agent replicas behind load balancer
   - Switch Reef backend to Redis pub/sub
   - Use Redis for session storage

2. **Database scaling:**
   - Read replicas for warehouse
   - Partitioning of fact tables by date
   - Connection pooling (PgBouncer)

3. **Cube.js scaling:**
   - Cube Store for pre-aggregations
   - Redis cache for query results
   - Multiple Cube.js instances

#### Vertical Scaling
- Increase PostgreSQL shared_buffers
- Add indexes on frequently queried dimensions
- Optimize dbt models with incremental builds

---

## Security

### Current Implementation
- **API Keys:** OpenAI key via environment variable
- **Cube.js Secret:** Hardcoded in docker-compose.yml
- **Database Passwords:** Hardcoded in docker-compose.yml
- **CORS:** Allows all origins (`allow_origins=["*"]`)

### Production Recommendations
1. Move secrets to secrets manager (AWS Secrets Manager, HashiCorp Vault)
2. Implement API authentication (JWT tokens)
3. Restrict CORS to frontend domain only
4. Use SSL/TLS for all database connections
5. Implement rate limiting on FastAPI endpoints
6. Audit logging for agent actions
7. Input sanitization for user queries

---

## Monitoring & Observability

### Current State
- **Logging:** Python logging module (INFO level)
- **Health Checks:** Docker Compose healthchecks (pg_isready)
- **Endpoint:** `/health` for Cube.js connectivity

### Recommended Additions
1. **Metrics:** Prometheus + Grafana
   - Agent response times
   - Cube.js query latency
   - Database query performance
   - Error rates by agent

2. **Tracing:** OpenTelemetry
   - End-to-end request tracing
   - Spore message flow visualization
   - Database query traces

3. **Alerting:**
   - Airflow DAG failures
   - Agent timeout errors
   - Database connection failures
   - Abnormal defect rates detected by Quality Inspector

4. **Dashboards:**
   - System health overview
   - Agent performance metrics
   - Data freshness (last EL/dbt run)
   - User query patterns

---

## Development Workflow

### Local Setup
1. Clone repository
2. Create `.env` file with OpenAI API key
3. Run `docker-compose up -d`
4. Wait 2 minutes for databases to initialize
5. Access frontend at http://localhost:3000

### Running Tests
```bash
# Backend tests (locally with venv)
./venv/bin/pytest tests/

# Specific test
./venv/bin/pytest tests/integration/agents/test_api.py::test_agents_endpoint -v

# With coverage
./venv/bin/pytest --cov=agents --cov-report=html
```

### Running dbt
```bash
# Inside Docker container
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform
docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform

# Locally (requires .dbt/profiles.yml)
dbt run --project-dir=dbt_transform
dbt test --project-dir=dbt_transform
```

### Adding New Agent
1. Create agent file: `agents/new_agent.py`
2. Define with `@agent` decorator
3. Specify `responds_to` message types
4. Import in `agents/app.py`
5. Add description to `/agents` endpoint
6. Write unit tests
7. Update documentation

### Adding New Cube
1. Create schema: `cubejs/schema/NewCube.js`
2. Define measures and dimensions
3. Map to dbt mart table
4. Restart Cube.js container
5. Update agent descriptions with new cube capabilities

---

## Access Points (When Running)

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Agents API | http://localhost:8000/docs | - |
| Cube.js Playground | http://localhost:4000 | - |
| Airflow | http://localhost:8080 | admin/admin |
| Warehouse DB | localhost:5435 | warehouse_user / warehouse_pass |
| Press Line A DB | localhost:5436 | press_a_user / press_a_pass |
| Press Line B DB | localhost:5437 | press_b_user / press_b_pass |
| Die Management DB | localhost:5438 | die_mgmt_user / die_mgmt_pass |

---

## Technology Versions

| Component | Version |
|-----------|---------|
| Python | 3.11 |
| FastAPI | 0.121+ |
| Praval | 0.7.16 |
| OpenAI | 2.8+ |
| Next.js | 14.1.0 |
| React | 18 |
| PostgreSQL | 15 |
| dbt | 1.7 |
| Cube.js | latest |
| Apache Airflow | 2.7.3 |
| Docker | 20.10+ |
| Docker Compose | 3.8 |

---

## Future Enhancements

### Short-term (Next Release)
1. Agent conversation memory (track context across sessions)
2. User authentication and authorization
3. Chart download/export functionality
4. Agent performance metrics dashboard
5. Retry logic for failed Cube.js queries

### Medium-term (3-6 months)
1. Voice input for queries (Whisper API)
2. Scheduled reports via email
3. Anomaly alert notifications (Slack, email)
4. Historical query cache (Redis)
5. Multi-language support (i18n)

### Long-term (6-12 months)
1. Predictive maintenance agent (ML model integration)
2. Real-time streaming data (Kafka integration)
3. Mobile app (React Native)
4. Multi-tenant architecture
5. Advanced visualizations (3D press simulations)

---

## References

- [Praval Documentation](https://github.com/anthropics/praval)
- [Cube.js Documentation](https://cube.dev/docs)
- [dbt Documentation](https://docs.getdbt.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [Airflow Documentation](https://airflow.apache.org/docs)

---

**Last Updated:** 2025-11-18
**Architecture Version:** 1.0
**Maintainer:** Development Team
