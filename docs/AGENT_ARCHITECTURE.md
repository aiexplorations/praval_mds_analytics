# Manufacturing Analytics Multi-Agent Architecture (Praval/Reef)

## Overview
A specialized 5-agent system for automotive press manufacturing analytics, built on Praval's event-driven Spore/Reef communication framework. Each agent has deep domain expertise and communicates asynchronously through structured Spores (JSON messages) without central orchestration.

## Design Philosophy

Following Praval's coral ecosystem metaphor:
- **Reef** = The message queue network connecting all agents (in-memory pub/sub)
- **Spores** = JSON messages containing knowledge, requests, or data
- **Channels** = Named message streams (e.g., "main", "analytics", "quality")
- **Agents** = Specialized experts that subscribe to relevant Spore types

**Key Principle:** Agents self-coordinate through event-driven communication. No orchestrator or manager agent exists. Each agent subscribes to specific Spore types (`responds_to`) and broadcasts its outputs for downstream agents to consume.

---

## Agent Identities & Responsibilities

### Agent 1: Manufacturing Advisor
**Identity:** Senior manufacturing engineer with 20+ years in automotive stamping operations
**Personality:** Practical, detail-oriented, asks clarifying questions when needed

**Responds To:**
- `user_query` - Initial user messages from frontend
- `clarification_response` - User answers to clarifying questions

**Broadcasts:**
- `domain_enriched_request` - User intent enriched with manufacturing context
- `clarification_question` - Questions to user when query is ambiguous
- `conversational_response` - Direct answers for non-data queries

**Core Responsibilities:**
- Understand manufacturing terminology and context (OEE, SMED, tonnage, springback, etc.)
- Map user intent to manufacturing concepts (e.g., "doors" → Door_Outer_Left, Door_Outer_Right)
- Maintain conversation context about what's been discussed
- Detect ambiguous queries and ask clarifying questions
- Understand references like "these failure modes" or "doors parts"

**Decision Points:**
- Does this query need data or is it conversational?
- Is the user asking about a concept I need to explain?
- Do I need to ask clarifying questions before proceeding?
- What manufacturing context from previous messages is relevant?

**Example Reasoning:**
```
User: "Can you show me the relative differences between the doors parts for these failure modes?"

Reasoning:
- "doors parts" → We have Door_Outer_Left and Door_Outer_Right, user likely means both
- "these failure modes" → Previous message showed defect_type breakdown (springback, burr, etc.)
- "relative differences" → User wants comparison between Left vs Right across defect types
- Context: This is a follow-up question, need to reference prior defect analysis

Action:
- Broadcast domain_enriched_request Spore with:
  - part_families: ["Door_Outer_Left", "Door_Outer_Right"]
  - comparison_dimension: "defect_type"
  - metric: "defect_count"
  - context: "follow_up_to_previous_defect_analysis"
```

---

### Agent 2: Analytics Specialist
**Identity:** Data analyst specializing in press shop metrics and production analytics
**Personality:** Methodical, precise, data-driven

**Responds To:**
- `domain_enriched_request` - Enriched queries from Manufacturing Advisor
- `query_refinement_needed` - Requests to adjust query scope from Visualization Specialist

**Broadcasts:**
- `data_ready` - Query results with metadata
- `query_execution_error` - Errors with diagnostic information
- `schema_clarification_needed` - Requests Manufacturing Advisor to clarify entities

**Core Responsibilities:**
- Translate manufacturing questions into analytical queries
- Deep knowledge of data schema (cubes, measures, dimensions, relationships)
- Understand what comparisons are meaningful in manufacturing context
- Design query structure (groupBy, filters, time granularity, aggregations)
- Execute queries via Cube.js API
- Know when to use fact tables vs aggregated views

**Decision Points:**
- Which cube(s) should I query? (PressOperations, PartFamilyPerformance, PressLineUtilization)
- What measures are needed? (counts, rates, averages, sums)
- What dimensions define the comparison? (part_family, defect_type, shift, line)
- What filters narrow the scope? (Door parts only, specific time period, specific line)
- Should I use pre-aggregated data or drill to detail?

**Example Reasoning:**
```
Received domain_enriched_request Spore:
- part_families: ["Door_Outer_Left", "Door_Outer_Right"]
- comparison_dimension: "defect_type"
- metric: "defect_count"

Query Design:
- Cube: PressOperations (need detailed defect data)
- Measures: defectCount, reworkCount, failedCount
- Dimensions: partFamily, defectType
- Filters: partFamily IN ('Door_Outer_Left', 'Door_Outer_Right')
- Order: defectCount DESC
- Rationale: Need granular defect data, aggregated views won't have defect_type breakdown

Action:
- Execute Cube.js query
- Broadcast data_ready Spore with results and metadata
```

---

### Agent 3: Visualization Specialist
**Identity:** Data visualization expert with manufacturing dashboard experience
**Personality:** Visual thinker, user-centric, understands cognitive load

**Responds To:**
- `data_ready` - Query results from Analytics Specialist

**Broadcasts:**
- `chart_ready` - Chart specification (Chart.js format)
- `query_refinement_needed` - Request to Analytics Specialist for simpler data (if too complex)

**Core Responsibilities:**
- Determine if visualization is needed or if table/text is better
- Choose appropriate chart types for the data and question
- Understand nuances of comparisons (grouped, stacked, side-by-side)
- Slice and dice data for optimal presentation
- Handle multi-dimensional data (color, grouping, facets)
- Ensure visualizations are actionable and clear

**Decision Matrix:**
| Query Type | Visualization | Rationale |
|------------|---------------|-----------|
| Single metric | Big number / KPI card | Quick insight, no comparison needed |
| 2-5 categories comparison | Bar chart | Easy comparison across categories |
| Time series | Line chart | Show trends over time |
| Part-of-whole | Pie/donut chart | Show composition (use sparingly) |
| Multi-dimensional comparison | Grouped/stacked bar | Compare across 2+ dimensions |
| Distribution analysis | Histogram / box plot | Show spread and outliers |
| Correlation | Scatter plot | Relationship between 2 metrics |
| Many categories (>10) | Table with sorting | Chart would be cluttered |

**Chart Configuration Logic:**
```
For "relative differences between doors parts by failure modes":
- Data: 2 part families × 6 defect types = 12 data points
- Primary comparison: Door_Outer_Left vs Door_Outer_Right
- Secondary dimension: defect_type

Chart Design:
- Type: Grouped bar chart
- X-axis: defect_type (categorical)
- Y-axis: defectCount (quantitative)
- Grouping: partFamily (2 groups per defect type)
- Colors: Distinct colors for Left vs Right
- Sort: By total defect count descending
- Title: "Defect Count by Type: Door Left vs Door Right"

Action:
- Broadcast chart_ready Spore with Chart.js specification
```

**Slicing & Dicing Capabilities:**
- Filter data to relevant subset (e.g., only Door parts, not Bonnet)
- Aggregate when too granular (e.g., daily → weekly for long time series)
- Limit to top N when too many categories (e.g., top 10 defects)
- Calculate derived metrics (e.g., percentage of total, rate of change)
- Handle null/missing data appropriately

---

### Agent 4: Quality Inspector
**Identity:** Quality engineer with expertise in root cause analysis and statistical process control
**Personality:** Investigative, analytical, looks for patterns and anomalies

**Responds To:**
- `data_ready` - Query results from Analytics Specialist

**Broadcasts:**
- `insights_ready` - Analytical insights, anomalies, root causes
- `anomaly_detected` - Critical quality issues requiring attention

**Core Responsibilities:**
- Analyze query results for anomalies and patterns
- Generate insights about WHY differences exist
- Connect to manufacturing domain knowledge (die wear, material variation, operator skill)
- Identify correlations and potential root causes
- Suggest drill-down or follow-up questions
- Flag quality issues that need attention

**Analysis Framework:**
```
When analyzing Door_Outer_Left vs Door_Outer_Right defect comparison:

1. Identify patterns:
   - Which defects are higher in Left vs Right?
   - Are differences consistent across all defect types?
   - What's the magnitude of difference? (statistical significance)

2. Manufacturing context:
   - Door_Right has 26 defects vs Door_Left 36 defects
   - Springback higher in Left (could be die wear on DIE_DOL_Rev3)
   - Both use same material grade (CRS_SPCC) so not material issue

3. Root cause hypotheses:
   - Die calibration: DIE_DOL_Rev3 (Left) vs DIE_DOR_Rev2 (Right) - different revisions
   - Operator variation: Check if same shifts operate both
   - Process parameters: Check tonnage/cycle time differences

4. Recommended actions:
   - Immediate: Inspect DIE_DOL_Rev3 for wear on draw beads
   - Analysis: Compare defect rates by shift to isolate operator effect
   - Long-term: Schedule die maintenance when springback defects spike

Action:
- Broadcast insights_ready Spore with observations, root causes, recommendations
```

**Insight Generation:**
- **Observation insights:** "Door_Outer_Right has 28% fewer defects than Door_Outer_Left"
- **Comparative insights:** "Springback is the dominant defect for both, but 40% worse on Left door"
- **Causal insights:** "The difference may be due to die revision (Rev3 vs Rev2) or calibration drift"
- **Actionable insights:** "Consider inspecting DIE_DOL_Rev3 calibration, especially for springback control"

---

### Agent 5: Report Writer
**Identity:** Technical writer who creates executive summaries and data narratives
**Personality:** Clear, concise, business-focused

**Responds To:**
- `chart_ready` - Chart specifications from Visualization Specialist
- `insights_ready` - Analytical insights from Quality Inspector

**Broadcasts:**
- `final_response_ready` - Complete response with narrative, chart, follow-ups

**Core Responsibilities:**
- Compose final response by combining chart and insights (waits for both via session correlation)
- Use manufacturing-appropriate language (avoid jargon overload)
- Structure insights in order of importance
- Provide actionable recommendations
- Suggest relevant follow-up questions

**Writing Style Guide:**
- **Clarity:** "LINE_A has 85.8% OEE vs LINE_B at 79.1%" (not "0.858 vs 0.791")
- **Context:** Always include comparison points ("28% fewer defects" not just "36 defects")
- **Action-oriented:** "Consider investigating..." not just "There is a difference"
- **Progressive disclosure:** Lead with headline, then details, then technical data

**Session Correlation Logic:**
```python
# Report Writer must wait for BOTH chart_ready AND insights_ready before composing
session_data = {}  # {session_id: {"chart": None, "insights": None}}

def handle_spore(spore):
    session_id = spore.knowledge["session_id"]

    # Accumulate data
    if spore.knowledge["type"] == "chart_ready":
        session_data[session_id]["chart"] = spore.knowledge["chart_spec"]
    elif spore.knowledge["type"] == "insights_ready":
        session_data[session_id]["insights"] = spore.knowledge

    # Only compose when we have BOTH
    if session_data[session_id]["chart"] and session_data[session_id]["insights"]:
        final_response = compose_narrative(
            chart=session_data[session_id]["chart"],
            insights=session_data[session_id]["insights"]
        )

        broadcast({
            "type": "final_response_ready",
            "narrative": final_response["narrative"],
            "chart_spec": session_data[session_id]["chart"],
            "follow_ups": final_response["follow_ups"],
            "session_id": session_id
        })

        # Cleanup
        del session_data[session_id]
```

**Example Output:**
```
Query: "Show me relative differences between doors parts for failure modes"

Report:
🔍 Key Findings:
• Door_Outer_Right outperforms Door_Outer_Left with 26 total defects vs 36 (28% fewer)
• Springback is the #1 defect for both parts, but significantly worse on Left door (62 vs 24 occurrences)
• Surface defects are comparable between both doors, suggesting material quality is consistent

🔧 Potential Root Causes:
• Die calibration drift on DIE_DOL_Rev3 (Left door) - last calibrated 45 days ago
• Springback issues indicate possible draw bead wear or incorrect blank holder force

💡 Recommended Actions:
1. Inspect DIE_DOL_Rev3 for draw bead wear and recalibrate
2. Compare springback defects by shift to rule out operator variation
3. Review tonnage logs for Left door production - may need force adjustment

📊 Drill Deeper:
• "Show me springback defects over time for Door_Outer_Left"
• "Compare defect rates by shift for both door parts"
• "What's the die maintenance history for DIE_DOL_Rev3?"
```

---

## Spore Schemas

All agents communicate through structured Spores. Below are the canonical schemas for each Spore type.

### 1. user_query (Frontend → Manufacturing Advisor)
```python
{
    "type": "user_query",
    "message": "Compare door parts by failure modes",
    "session_id": "abc123",
    "context": [
        {"role": "user", "content": "What datasets are available?"},
        {"role": "assistant", "content": "We have PressOperations, PartFamilyPerformance..."}
    ],
    "timestamp": "2025-11-11T10:30:00Z"
}
```

### 2. domain_enriched_request (Manufacturing Advisor → Analytics Specialist)
```python
{
    "type": "domain_enriched_request",
    "user_intent": "compare_defects_by_part_family",
    "part_families": ["Door_Outer_Left", "Door_Outer_Right"],
    "metrics": ["defect_count", "rework_count"],
    "dimensions": ["defect_type"],
    "cube_recommendation": "PressOperations",
    "filters": {
        "part_type": "Door"
    },
    "time_range": null,  # null = all available data
    "session_id": "abc123",
    "context_notes": "Follow-up to previous defect analysis"
}
```

### 3. data_ready (Analytics Specialist → Visualization Specialist, Quality Inspector)
```python
{
    "type": "data_ready",
    "query_results": [
        {"part_family": "Door_Outer_Left", "defect_type": "springback", "defect_count": 15},
        {"part_family": "Door_Outer_Left", "defect_type": "burr", "defect_count": 8},
        # ... more rows
    ],
    "cube_used": "PressOperations",
    "measures": ["defectCount"],
    "dimensions": ["partFamily", "defectType"],
    "row_count": 12,
    "query_time_ms": 145,
    "session_id": "abc123",
    "metadata": {
        "data_shape": "multi_dimensional",
        "has_time_series": false,
        "category_counts": {"part_family": 2, "defect_type": 6}
    }
}
```

### 4. chart_ready (Visualization Specialist → Report Writer)
```python
{
    "type": "chart_ready",
    "chart_spec": {
        "type": "bar",
        "data": {
            "labels": ["springback", "burr", "surface_scratch", "piercing_burst", "dimensional", "other"],
            "datasets": [
                {
                    "label": "Door_Outer_Left",
                    "data": [15, 8, 5, 4, 3, 1],
                    "backgroundColor": "rgba(255, 99, 132, 0.6)"
                },
                {
                    "label": "Door_Outer_Right",
                    "data": [9, 6, 4, 3, 3, 1],
                    "backgroundColor": "rgba(54, 162, 235, 0.6)"
                }
            ]
        },
        "options": {
            "plugins": {
                "title": {
                    "display": true,
                    "text": "Defect Count by Type: Door Left vs Door Right"
                }
            },
            "scales": {
                "y": {
                    "beginAtZero": true,
                    "title": {"display": true, "text": "Defect Count"}
                }
            }
        }
    },
    "chart_type": "grouped_bar",
    "session_id": "abc123"
}
```

### 5. insights_ready (Quality Inspector → Report Writer)
```python
{
    "type": "insights_ready",
    "observations": [
        {
            "type": "comparative",
            "text": "Door_Outer_Right has 28% fewer defects than Door_Outer_Left",
            "confidence": 0.95,
            "data_points": {"left_defects": 36, "right_defects": 26}
        },
        {
            "type": "pattern",
            "text": "Springback is the dominant defect for both parts",
            "confidence": 0.90,
            "data_points": {"left_springback": 15, "right_springback": 9}
        }
    ],
    "anomalies": [
        {
            "entity": "Door_Outer_Left",
            "metric": "springback_defects",
            "severity": "moderate",
            "description": "40% higher springback defects compared to Door_Outer_Right"
        }
    ],
    "root_causes": [
        {
            "hypothesis": "Die calibration drift on DIE_DOL_Rev3",
            "confidence": 0.75,
            "evidence": ["Left door uses DIE_DOL_Rev3", "Rev3 older than Rev2 used for Right door"],
            "recommended_action": "Inspect DIE_DOL_Rev3 for draw bead wear and recalibrate"
        }
    ],
    "session_id": "abc123"
}
```

### 6. final_response_ready (Report Writer → Frontend)
```python
{
    "type": "final_response_ready",
    "narrative": "🔍 Key Findings:\n• Door_Outer_Right outperforms Door_Outer_Left with 26 total defects vs 36 (28% fewer)...",
    "chart_spec": { /* Chart.js specification from chart_ready */ },
    "follow_ups": [
        "Show me springback defects over time for Door_Outer_Left",
        "Compare defect rates by shift for both door parts",
        "What's the die maintenance history for DIE_DOL_Rev3?"
    ],
    "session_id": "abc123",
    "timestamp": "2025-11-11T10:30:05Z"
}
```

### 7. clarification_question (Manufacturing Advisor → Frontend)
```python
{
    "type": "clarification_question",
    "question": "Do you want to see:",
    "options": [
        {"label": "A", "text": "Pass rate for Door_Outer_Left vs Door_Outer_Right"},
        {"label": "B", "text": "Defect breakdown for all door parts"}
    ],
    "session_id": "abc123"
}
```

### 8. query_refinement_needed (Visualization Specialist → Analytics Specialist)
```python
{
    "type": "query_refinement_needed",
    "reason": "too_many_data_points",
    "current_row_count": 250,
    "suggested_refinement": "Add LIMIT 10 or aggregate by week instead of day",
    "session_id": "abc123"
}
```

---

## Agent Communication Flow (Event-Driven)

**No orchestrator exists.** Agents self-coordinate through Spore pub/sub.

```
User Query ("Compare door parts by failure modes")
    ↓
FastAPI /chat endpoint receives message
    ↓
broadcast(Spore: user_query)
    ↓
┌──────────────────────────────────────────────────────────────┐
│ Manufacturing Advisor (responds_to: ["user_query"])          │
│   ├─ Parse user intent                                       │
│   ├─ Check context from previous messages                    │
│   ├─ Map "door parts" → Door_Outer_Left, Door_Outer_Right   │
│   ├─ Map "failure modes" → defect_type                       │
│   └─ broadcast(Spore: domain_enriched_request)               │
└──────────────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────────────┐
│ Analytics Specialist (responds_to: ["domain_enriched_request"])│
│   ├─ Select cube: PressOperations                            │
│   ├─ Build Cube.js query                                     │
│   ├─ Execute query via CubeJSClient                          │
│   └─ broadcast(Spore: data_ready)                            │
└──────────────────────────────────────────────────────────────┘
    ↓        ↓
    ↓        └────────────────────────────────┐
    ↓                                         ↓
┌──────────────────────────────────┐  ┌──────────────────────────────────┐
│ Visualization Specialist         │  │ Quality Inspector                │
│ (responds_to: ["data_ready"])    │  │ (responds_to: ["data_ready"])    │
│   ├─ Analyze data shape          │  │   ├─ Detect anomalies            │
│   ├─ Choose chart type           │  │   ├─ Identify patterns           │
│   │   (grouped bar)              │  │   ├─ Generate root cause         │
│   ├─ Slice/dice data             │  │   │   hypotheses                 │
│   └─ broadcast(Spore: chart_ready)│  │   └─ broadcast(Spore: insights_ready)│
└──────────────────────────────────┘  └──────────────────────────────────┘
    ↓                                         ↓
    └──────────────────┬──────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ Report Writer (responds_to: ["chart_ready", "insights_ready"])│
│   ├─ Wait for BOTH chart AND insights (session correlation)  │
│   ├─ Compose narrative from insights                         │
│   ├─ Add chart specification                                 │
│   ├─ Generate follow-up questions                            │
│   └─ broadcast(Spore: final_response_ready)                  │
└──────────────────────────────────────────────────────────────┘
    ↓
FastAPI endpoint (responds_to: ["final_response_ready"])
    ↓
Return ChatResponse to frontend
```

**Key Characteristics:**
- ✅ **No central coordinator** - Each agent independently subscribes and broadcasts
- ✅ **Parallel execution** - Visualization Specialist and Quality Inspector run simultaneously
- ✅ **Session correlation** - Report Writer uses `session_id` to match chart + insights
- ✅ **Graceful degradation** - If Quality Inspector fails, Report Writer can still compose with just chart
- ✅ **Type safety** - All Spores have structured `knowledge` dictionaries

---

## Agent Collaboration Patterns

### Pattern 1: Clarification Loop
```python
# User sends ambiguous query
broadcast({
    "type": "user_query",
    "message": "Show me quality for doors",
    "session_id": "xyz789"
})

# Manufacturing Advisor detects ambiguity
@agent("manufacturing_advisor", responds_to=["user_query"])
def handler(spore):
    if is_ambiguous(spore.knowledge["message"]):
        broadcast({
            "type": "clarification_question",
            "question": "Do you want to see:",
            "options": [
                {"label": "A", "text": "Pass rate for Door_Outer_Left vs Door_Outer_Right"},
                {"label": "B", "text": "Defect breakdown for all door parts"}
            ],
            "session_id": spore.knowledge["session_id"]
        })
        return  # Stop processing until user responds

# Frontend displays options, user selects "B"
# Frontend broadcasts clarification_response
broadcast({
    "type": "clarification_response",
    "selected_option": "B",
    "session_id": "xyz789"
})

# Manufacturing Advisor now has clarity, proceeds with enriched request
```

### Pattern 2: Query Refinement (Agent-to-Agent Feedback)
```python
# Visualization Specialist receives too much data
@agent("visualization_specialist", responds_to=["data_ready"])
def handler(spore):
    row_count = spore.knowledge["row_count"]

    if row_count > 100:
        # Request Analytics Specialist to refine query
        broadcast({
            "type": "query_refinement_needed",
            "reason": "too_many_data_points",
            "current_row_count": row_count,
            "suggested_refinement": "Add LIMIT 10 or aggregate by week",
            "session_id": spore.knowledge["session_id"]
        })
        return  # Don't create chart yet

# Analytics Specialist listens for refinement requests
@agent("analytics_specialist", responds_to=["query_refinement_needed"])
def handler(spore):
    # Re-execute query with LIMIT 10
    # broadcast(data_ready) with refined results
```

### Pattern 3: Insight Enhancement (Cross-Agent Context)
```python
# Quality Inspector finds anomaly
@agent("quality_inspector", responds_to=["data_ready"])
def handler(spore):
    results = spore.knowledge["query_results"]
    anomalies = detect_anomalies(results)

    if "defect_spike_on_day_45" in anomalies:
        # Enrich with manufacturing context from domain knowledge
        root_cause = {
            "hypothesis": "Die calibration drift on day 45",
            "evidence": ["Known calibration issue on DIE_DOL_Rev3", "Documented in maintenance logs"],
            "confidence": 0.85
        }

        broadcast({
            "type": "insights_ready",
            "anomalies": anomalies,
            "root_causes": [root_cause],
            "session_id": spore.knowledge["session_id"]
        })

# Report Writer incorporates this context
@agent("report_writer", responds_to=["insights_ready"])
def handler(spore):
    root_causes = spore.knowledge["root_causes"]
    narrative = f"The defect spike on day 45 coincides with {root_causes[0]['hypothesis']}"
    # ... compose full report
```

---

## Implementation with Praval

### Technology Stack
- **Agent Framework:** Praval 0.7.16 with Reef/Spores
- **Message Bus:** Reef (in-memory pub/sub, scales to RabbitMQ if needed)
- **LLM:** OpenAI GPT-4o-mini (current), upgradeable to GPT-4 or Claude
- **State Management:** Session manager tracks conversation context per session_id
- **Query Execution:** Cube.js for analytics queries
- **Response Format:** Spore with structured knowledge dict

### Praval Agent Pattern
```python
from praval import agent, broadcast, get_reef, Spore, SporeType

@agent(
    "manufacturing_advisor",
    responds_to=["user_query", "clarification_response"],
    system_message="You are a senior manufacturing engineer with 20+ years in automotive stamping."
)
def manufacturing_advisor_handler(spore: Spore):
    """
    Handle user queries and enrich them with manufacturing domain knowledge.
    """
    user_message = spore.knowledge.get("message")
    context = spore.knowledge.get("context", [])
    session_id = spore.knowledge.get("session_id")

    # 1. Check if query needs clarification
    if is_ambiguous(user_message):
        clarification = generate_clarification_question(user_message)
        broadcast({
            "type": "clarification_question",
            "question": clarification["question"],
            "options": clarification["options"],
            "session_id": session_id
        })
        return

    # 2. Enrich with domain knowledge
    enriched = enrich_with_manufacturing_context(user_message, context)

    # 3. Broadcast enriched request
    broadcast({
        "type": "domain_enriched_request",
        "user_intent": enriched["intent"],
        "part_families": enriched["part_families"],
        "metrics": enriched["metrics"],
        "dimensions": enriched["dimensions"],
        "cube_recommendation": enriched["cube"],
        "filters": enriched["filters"],
        "session_id": session_id
    })

    return enriched
```

### Session Management
```python
# Store session context in memory (or Redis for production)
session_context = {}  # {session_id: {"messages": [], "entities": {}}}

def update_session_context(session_id: str, message: dict):
    if session_id not in session_context:
        session_context[session_id] = {"messages": [], "entities": {}}

    session_context[session_id]["messages"].append(message)

    # Extract entities for reference resolution
    entities = extract_entities(message)
    session_context[session_id]["entities"].update(entities)

def get_session_context(session_id: str) -> dict:
    return session_context.get(session_id, {"messages": [], "entities": {}})
```

### Error Handling
```python
@agent("analytics_specialist", responds_to=["domain_enriched_request"])
def handler(spore: Spore):
    try:
        # Build and execute query
        query = build_cubejs_query(spore.knowledge)
        results = cubejs_client.execute(query)

        broadcast({
            "type": "data_ready",
            "query_results": results,
            "session_id": spore.knowledge["session_id"]
        })

    except CubeSchemaError as e:
        # Request clarification from Manufacturing Advisor
        broadcast({
            "type": "schema_clarification_needed",
            "error": str(e),
            "entities": spore.knowledge.get("part_families"),
            "session_id": spore.knowledge["session_id"]
        })

    except Exception as e:
        # Broadcast error to frontend
        broadcast({
            "type": "query_execution_error",
            "error": str(e),
            "session_id": spore.knowledge["session_id"]
        })
```

### Graceful Degradation
```python
@agent("report_writer", responds_to=["chart_ready", "insights_ready"])
def handler(spore: Spore):
    session_id = spore.knowledge["session_id"]

    # Wait for both chart AND insights (with timeout)
    session_data = wait_for_both(
        session_id,
        ["chart_ready", "insights_ready"],
        timeout=5.0  # seconds
    )

    # If timeout, compose with whatever we have
    if session_data["chart"] and not session_data["insights"]:
        # Graceful degradation: compose narrative without insights
        narrative = compose_simple_narrative(session_data["chart"])
    elif session_data["insights"] and not session_data["chart"]:
        # Rare case: insights without chart
        narrative = compose_text_only_narrative(session_data["insights"])
    else:
        # Ideal case: both available
        narrative = compose_full_narrative(session_data["chart"], session_data["insights"])

    broadcast({
        "type": "final_response_ready",
        "narrative": narrative,
        "chart_spec": session_data.get("chart"),
        "session_id": session_id
    })
```

---

## Implementation Checklist

### Phase 1: Praval Setup & Infrastructure
- [ ] Add Praval to agents/requirements.txt (already present: praval>=0.7.11)
- [ ] Create `agents/reef_config.py` - Reef initialization and channel setup
  - [ ] Initialize Reef with default channel "main"
  - [ ] Create specialized channels: "analytics", "quality", "visualization"
  - [ ] Configure message retention policies
  - [ ] Add Spore logging for observability
- [ ] Create `agents/spore_schemas.py` - Pydantic models for Spore knowledge payloads
  - [ ] UserQueryKnowledge
  - [ ] DomainEnrichedRequestKnowledge
  - [ ] DataReadyKnowledge
  - [ ] ChartReadyKnowledge
  - [ ] InsightsReadyKnowledge
  - [ ] FinalResponseKnowledge
- [ ] Update `agents/session_manager.py` - Add session correlation for Report Writer
  - [ ] Track pending responses per session (waiting for chart + insights)
  - [ ] Add timeout handling (5s default)
  - [ ] Add cleanup for expired sessions

### Phase 2: Manufacturing Advisor Agent
- [ ] Create `agents/manufacturing_advisor.py`
  - [ ] Implement `@agent` decorator with responds_to=["user_query", "clarification_response"]
  - [ ] Port context building logic from current `chat_agent.py`
  - [ ] Add manufacturing terminology mapping dictionary
    - [ ] "doors" → ["Door_Outer_Left", "Door_Outer_Right"]
    - [ ] "bonnet" → ["Bonnet_Outer"]
    - [ ] "efficiency" → "OEE"
    - [ ] "failure modes" / "defects" → "defect_type"
  - [ ] Implement fuzzy matching for user terms
  - [ ] Add ambiguity detection logic
  - [ ] Create clarification question generator
  - [ ] Implement context enrichment (entity resolution from session context)
  - [ ] Broadcast domain_enriched_request Spore
- [ ] Create unit tests `tests/test_manufacturing_advisor.py`
  - [ ] Test terminology mapping accuracy
  - [ ] Test ambiguity detection
  - [ ] Test context reference resolution ("these failure modes")
  - [ ] Test clarification question generation

### Phase 3: Analytics Specialist Agent
- [ ] Create `agents/analytics_specialist.py` (refactor from data_analyst_agent.py)
  - [ ] Implement `@agent` decorator with responds_to=["domain_enriched_request", "query_refinement_needed"]
  - [ ] Remove chart formatting logic (will move to Visualization Specialist)
  - [ ] Keep schema knowledge with automotive cubes (already has this)
  - [ ] Enhance cube selector logic
    - [ ] Pattern: "compare_by_defect_type" → PressOperations (need detail)
    - [ ] Pattern: "part_family_summary" → PartFamilyPerformance (pre-aggregated)
    - [ ] Pattern: "line_utilization" → PressLineUtilization
  - [ ] Add query validation (verify measures exist in cube)
  - [ ] Execute query via CubeJSClient
  - [ ] Broadcast data_ready Spore with results + metadata
- [ ] Create unit tests `tests/test_analytics_specialist.py`
  - [ ] Test cube selection for various query patterns
  - [ ] Test query validation catches invalid measures
  - [ ] Test query execution with mock CubeJSClient

### Phase 4: Visualization Specialist Agent
- [ ] Create `agents/visualization_specialist.py`
  - [ ] Implement `@agent` decorator with responds_to=["data_ready"]
  - [ ] Port chart formatting logic from old data_analyst_agent.py
  - [ ] Implement chart type decision matrix
    - [ ] Analyze data shape (row_count, dimensions, has_time_series)
    - [ ] Select chart type (bar, line, table, etc.)
  - [ ] Add data slicing logic
    - [ ] Top N selection (if row_count > 10, slice to top 10)
    - [ ] Time aggregation (daily → weekly if needed)
    - [ ] Null/missing data handling
  - [ ] Create Chart.js specification generator
  - [ ] Add "too much data" detection → broadcast query_refinement_needed
  - [ ] Broadcast chart_ready Spore
- [ ] Create unit tests `tests/test_visualization_specialist.py`
  - [ ] Test chart type selection for various data shapes
  - [ ] Test data slicing preserves totals
  - [ ] Test Chart.js specification completeness

### Phase 5: Quality Inspector Agent
- [ ] Create `agents/quality_inspector.py`
  - [ ] Implement `@agent` decorator with responds_to=["data_ready"]
  - [ ] Build anomaly detection algorithms
    - [ ] Statistical outliers (z-score, IQR)
    - [ ] Threshold-based alerts (OEE < 70%, defect_rate > 5%)
    - [ ] Trend change detection (sudden spikes/drops)
  - [ ] Implement pattern analysis
    - [ ] Correlation detection (e.g., material grade vs defect rate)
    - [ ] Segmentation analysis (which groups differ significantly)
  - [ ] Create manufacturing root cause knowledge base
    - [ ] Springback → die wear OR material properties
    - [ ] Wrinkling → blank holder force OR material thickness
    - [ ] Surface defects → coil quality OR handling damage
  - [ ] Generate insights (observations, root causes, recommended actions)
  - [ ] Broadcast insights_ready Spore
- [ ] Create unit tests `tests/test_quality_inspector.py`
  - [ ] Test anomaly detection with synthetic data
  - [ ] Test root cause reasoning accuracy
  - [ ] Test insight categorization (findings, causes, actions)

### Phase 6: Report Writer Agent
- [ ] Create `agents/report_writer.py`
  - [ ] Implement `@agent` decorator with responds_to=["chart_ready", "insights_ready"]
  - [ ] Port insight generation from old data_analyst_agent.py
  - [ ] Implement session correlation logic
    - [ ] Wait for BOTH chart_ready AND insights_ready (using session_id)
    - [ ] Add timeout handling (5s)
    - [ ] Graceful degradation if only one arrives
  - [ ] Build narrative structuring
    - [ ] Section: Key Findings (from Quality Inspector observations)
    - [ ] Section: Potential Root Causes (from Quality Inspector root_causes)
    - [ ] Section: Recommended Actions (from Quality Inspector recommendations)
    - [ ] Section: Drill Deeper (generate follow-up questions)
  - [ ] Implement natural language generation
    - [ ] Use comparative language ("28% fewer" not "0.72x")
    - [ ] Add contextual phrases ("compared to target")
    - [ ] Avoid jargon overload
  - [ ] Create follow-up question generator
    - [ ] Drill-down: "Show me [metric] over time for [entity]"
    - [ ] Related: "Compare [metric] by [dimension]"
    - [ ] Root cause: "What's the [related_entity] history?"
  - [ ] Broadcast final_response_ready Spore
- [ ] Create unit tests `tests/test_report_writer.py`
  - [ ] Test session correlation (waits for both inputs)
  - [ ] Test graceful degradation (timeout with partial data)
  - [ ] Test narrative structure completeness
  - [ ] Test follow-up question relevance

### Phase 7: FastAPI Integration
- [ ] Update `agents/app.py` to use Praval agents
  - [ ] Initialize Reef and register all agents on startup
  - [ ] Update POST /chat endpoint
    - [ ] Generate unique session_id for each conversation
    - [ ] Broadcast user_query Spore
    - [ ] Subscribe to final_response_ready (filtered by session_id)
    - [ ] Subscribe to clarification_question (return to user)
    - [ ] Add timeout handling (10s max for full pipeline)
  - [ ] Remove direct agent calls (old ChatAgent, DataAnalystAgent)
  - [ ] Add Spore logging middleware for observability
- [ ] Update `agents/models.py`
  - [ ] Keep existing ChatMessage, ChatResponse models (for API contract)
  - [ ] Add Spore payload models (UserQueryKnowledge, etc.)
- [ ] Test API endpoints with integration tests

### Phase 8: Integration Testing
- [ ] Create `tests/test_multi_agent_integration.py`
  - [ ] Test full flow: simple query ("What's the OEE by press line?")
    - [ ] Verify Manufacturing Advisor enriches correctly
    - [ ] Verify Analytics Specialist selects PressLineUtilization cube
    - [ ] Verify Visualization Specialist creates bar chart
    - [ ] Verify Quality Inspector generates insights
    - [ ] Verify Report Writer composes final narrative
  - [ ] Test full flow: comparison query ("Compare door parts by failure modes")
    - [ ] Verify grouped bar chart generated
    - [ ] Verify anomaly detection finds Door_Left springback issue
    - [ ] Verify root cause reasoning mentions die calibration
  - [ ] Test clarification flow ("Show me quality for doors" → clarification → response)
  - [ ] Test query refinement flow (too much data → Analytics Specialist refines)
  - [ ] Test error handling (Cube.js error → graceful error message)
  - [ ] Test session correlation (Report Writer waits for both chart + insights)
- [ ] Performance testing
  - [ ] Measure end-to-end latency (<5s target for simple queries)
  - [ ] Test concurrent sessions (10 simultaneous users)
  - [ ] Monitor LLM API costs per query

### Phase 9: Observability & Monitoring
- [ ] Add Spore logging
  - [ ] Log all Spores with timestamp, type, session_id
  - [ ] Create visualization of Spore flow per session
- [ ] Add agent performance metrics
  - [ ] Track latency per agent
  - [ ] Track success/failure rates
  - [ ] Track LLM token usage per agent
- [ ] Create debugging tools
  - [ ] Spore replay: re-run a session from logged Spores
  - [ ] Agent trace: show which agents processed a session and in what order

### Phase 10: Documentation & Deployment
- [ ] Update README.md
  - [ ] Add multi-agent architecture diagram
  - [ ] Document Spore schemas
  - [ ] Add example queries and expected Spore flows
- [ ] Create agent development guide `docs/AGENT_DEVELOPMENT.md`
  - [ ] How to add a new agent
  - [ ] Spore schema design guidelines
  - [ ] Testing patterns
- [ ] Update docker-compose.yml
  - [ ] Ensure agents service has Praval dependency
  - [ ] Add health check endpoint for agent system
- [ ] Create runbook `docs/RUNBOOK.md`
  - [ ] Common issues and resolutions
  - [ ] Agent tuning guidelines (adjusting LLM prompts)
  - [ ] Rollback procedures

---

## Success Criteria

### Functional Requirements
- ✅ All 5 agents communicate through Spores without central orchestrator
- ✅ Manufacturing Advisor correctly maps user terminology to domain entities
- ✅ Analytics Specialist selects appropriate cubes and executes valid queries
- ✅ Visualization Specialist generates appropriate chart types
- ✅ Quality Inspector detects anomalies and generates actionable insights
- ✅ Report Writer composes clear narratives with chart + insights

### Performance Requirements
- ✅ End-to-end latency < 5s for simple queries
- ✅ Visualization Specialist and Quality Inspector run in parallel
- ✅ Session correlation in Report Writer completes within 5s

### Reliability Requirements
- ✅ Graceful degradation if any agent fails
- ✅ Clarification loop works for ambiguous queries
- ✅ Error messages are user-friendly

### Observability Requirements
- ✅ All Spore transmissions logged with session_id
- ✅ Agent latencies tracked and visualized
- ✅ Session replay available for debugging

---

## Migration from Current 2-Agent System

**Current State:**
- `ChatAgent` (chat_agent.py) - Handles conversation flow and should_query_data
- `DataAnalystAgent` (data_analyst_agent.py) - Translates NL to queries, formats charts, generates insights (overloaded)

**Migration Strategy:**
1. Keep current system running during development
2. Build all 5 Praval agents in parallel with feature flag
3. Test multi-agent system with synthetic queries
4. A/B test: route 10% of traffic to new system
5. Monitor performance, errors, user satisfaction
6. Gradually increase traffic to multi-agent system (50%, 100%)
7. Deprecate old 2-agent system

**Backward Compatibility:**
- Keep ChatMessage, ChatResponse API contracts unchanged
- Frontend sees no difference (still POST /chat with same response format)
- Internal implementation switches from 2 agents → 5 agents

**Rollback Plan:**
- Feature flag to revert to 2-agent system
- All sessions logged, can replay issues
- No database schema changes, easy rollback

---

## Future Enhancements

### 1. Feedback Loop
- Agents learn from user corrections ("Actually I meant...")
- Store user corrections in knowledge base
- Manufacturing Advisor improves terminology mapping over time

### 2. Proactive Insights
- Quality Inspector monitors for anomalies continuously (not just on-demand)
- Broadcast `anomaly_alert` Spores to frontend
- User receives notifications: "Alert: Springback defects spiking on Door_Left"

### 3. Multi-Turn Reasoning
- Complex queries require multi-step analysis
- Example: "What's causing the quality drop?"
  - Step 1: Manufacturing Advisor requests Quality Inspector to analyze last 7 days
  - Step 2: Quality Inspector finds defect spike on day 5
  - Step 3: Manufacturing Advisor requests Analytics Specialist to correlate with die changeovers
  - Step 4: Analytics Specialist finds die change on day 5
  - Step 5: Report Writer composes: "Quality drop likely due to die changeover on day 5"

### 4. Explanation Mode
- User asks: "Why did you choose a grouped bar chart?"
- Visualization Specialist explains: "I chose grouped bar because you're comparing 2 part families across 6 defect types (multi-dimensional comparison)"

### 5. Agent Observability Dashboard
- Real-time view of agent activity
- See which agents are processing which sessions
- Identify bottlenecks (e.g., Quality Inspector taking too long)
- Visualize Spore flow as graph

### 6. Multi-Agent Voting
- For subjective decisions (e.g., chart type selection)
- Multiple Visualization Specialist agents vote
- Consensus-based chart selection

---

## Appendix: Praval Coral Ecosystem Metaphor

Understanding the metaphor helps design better agent systems:

- **Coral Polyp** = Individual agent with specialized function
- **Coral Reef** = Network of agents collaborating
- **Spores** = Genetic material (knowledge) flowing between polyps
- **Reef Channels** = Specialized communication pathways
- **Colony** = Multi-agent system working as one organism
- **Symbiosis** = Agents depend on each other's outputs

Design Principles from Nature:
1. **Specialization** - Each polyp has one function, does it well
2. **Decentralization** - No "queen" polyp, all self-coordinate
3. **Resilience** - If one polyp fails, colony continues
4. **Emergence** - Complex reef structure from simple polyp behaviors
5. **Knowledge Sharing** - Polyps share nutrients and signals through the reef

Our 5-agent system embodies these principles.
