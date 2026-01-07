# Praval Manufacturing Analytics System - Development Guide

## Project Overview

AI-powered analytics platform for automotive press manufacturing using multi-agent intelligence (Praval framework). Tracks production metrics for 2 press lines (800T and 1200T) producing door and bonnet panels.

## Core Architecture

### Data Flow
Source DBs → EL Pipeline → Data Warehouse → dbt Transformations → Cube.js Semantic Layer → AI Agents → Frontend

### Key Components

1. **agents/** - FastAPI backend with 5 Praval agents using event-driven Spore/Reef architecture
   - Manufacturing Advisor: Domain expertise and terminology mapping
   - Analytics Specialist: Query translation and Cube.js execution
   - Visualization Specialist: Chart type selection
   - Quality Inspector: Anomaly detection and root cause analysis
   - Report Writer: Narrative composition and insights
   - **No central orchestrator** - agents self-coordinate via pub/sub messaging

2. **el_pipeline/** - Extract-Load pipeline (no transformation)
   - Simple EL pattern from source PostgreSQL databases to warehouse
   - CLI interface: `python el_pipeline/cli.py` or `python run_el_pipeline.py`

3. **dbt_transform/** - Data transformation layer (dbt 1.7)
   - 4 staging models (data cleansing)
   - 2 intermediate models (business logic)
   - 7+ mart models (analytics-ready)
   - Run: `docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform`

4. **cubejs/** - Semantic layer with 3 cubes (PressOperations, PartFamilyPerformance, PressLineUtilization)

5. **frontend/** - Next.js 14 chat interface

6. **airflow/** - Orchestration DAGs

## Development Practices

### Virtual Environment
- **Always use the venv** at `./venv/` for local Python development
- Install dependencies: `./venv/bin/pip install -r requirements.txt`
- Run tests: `./venv/bin/pytest`

### Testing
- Test structure: `tests/el_pipeline/`, `agents/tests/`
- Markers: unit, integration, slow
- Run locally: `./venv/bin/pytest`
- Run in Docker: `docker exec analytics-agents ./venv/bin/pytest`
- dbt tests: `docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform`

### Docker Development
- Start system: `docker-compose up -d`
- View logs: `docker logs analytics-agents --follow`
- Services: 4 PostgreSQL DBs, Airflow, Cube.js, Agents API, Frontend
- All services defined in `docker-compose.yml`

### Configuration
- `.env` - OpenAI API key, database connections
- `.dbt/profiles.yml` - dbt warehouse connection
- `docker/postgres/*/init.sql` - Database initialization scripts

## Important Conventions

### Multi-Agent Communication (Praval)
- Event-driven via Spores (JSON messages between agents)
- Session correlation using `session_id` for multi-turn conversations
- Agents subscribe to message types with `@responds_to` decorator
- Parallel execution: Viz and Quality agents run simultaneously
- Graceful degradation: System works even if individual agents fail

### Code Quality Standards
- Type hints required (Pydantic models throughout)
- PEP-8 formatting
- Async/await patterns in FastAPI
- Structured logging (not print statements)
- Comprehensive error handling

### Data Pipeline Pattern
- No transformation during EL - pure extraction and loading
- All business logic in dbt layer
- Foreign Data Wrappers connect source DBs to warehouse
- Semantic layer (Cube.js) ensures consistent metrics

## Domain Knowledge

### Manufacturing Context
- **Press Lines**: Line A (800T, door panels), Line B (1200T, bonnet panels)
- **Part Families**: Door_Outer_Left, Door_Outer_Right, Bonnet_Outer
- **Key Metrics**: OEE, defect rates, first pass yield, cycle time, tonnage
- **Die Management**: 4 dies with changeover tracking (SMED metrics)
- **Material Traceability**: 126 coils from 3 suppliers

### OEE Calculation
```
OEE = Availability × Performance × Quality Rate
- Availability: Uptime / Planned production time
- Performance: Actual output / Target output
- Quality Rate: Good parts / Total parts produced
```

## Development Workflow

### Adding New Features
1. Create feature branch (never work directly on main)
2. Implement with tests
3. Run test suite to validate
4. Update documentation if needed
5. Create PR with clear description

### Modifying Agents
1. Agent logic in `agents/` directory (each agent is a module)
2. Message schemas in `agents/spore_schemas.py`
3. Reef config in `agents/reef_config.py`
4. Test agent interactions with unit tests
5. Validate end-to-end with Docker setup

### Adding Data Sources
1. Create database init script in `docker/postgres/<source-name>/`
2. Add service to `docker-compose.yml`
3. Create Foreign Data Wrapper in warehouse `init.sql`
4. Add source to `dbt_transform/models/staging/sources.yml`
5. Create staging model in dbt
6. Create Cube.js schema

### Running Full Pipeline
```bash
# Start infrastructure
docker-compose up -d

# Wait for databases to initialize (~2 minutes)

# Run EL pipeline (if needed)
docker exec analytics-agents ./venv/bin/python run_el_pipeline.py

# Run dbt transformations
docker exec analytics-agents ./venv/bin/dbt run --project-dir=dbt_transform

# Test dbt models
docker exec analytics-agents ./venv/bin/dbt test --project-dir=dbt_transform
```

## Important Files

- `README.md` - System overview and quick start guide
- `docs/AGENT_ARCHITECTURE.md` - Complete multi-agent design documentation
- `docs/AUTOMOTIVE_DATASET.md` - Dataset specification
- `agents/spore_schemas.py` - Message contract definitions between agents
- `dbt_transform/models/` - All data transformation logic
- `docker-compose.yml` - Infrastructure definition

## Access Points (when running)

- Frontend: http://localhost:3000
- Cube.js Playground: http://localhost:4000
- Airflow: http://localhost:8080 (admin/admin)
- Agents API: http://localhost:8000/docs

## Testing Philosophy

- Write real, functional tests (no mock placeholders)
- Test in proper environment (venv or Docker)
- Cover edge cases and error conditions
- Integration tests for agent communication
- dbt tests for data quality

## Deployment Notes

- Production uses Docker Compose
- All services containerized
- Volume persistence for databases
- Health checks on critical services
- Network isolation via mds-network
