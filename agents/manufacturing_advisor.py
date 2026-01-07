"""
Manufacturing Advisor Agent.

Senior manufacturing engineer with 20+ years in automotive stamping.
Understands manufacturing terminology and enriches user queries with domain context.
"""
import json
import logging
from typing import Dict, List, Any
from praval import agent, broadcast, Spore
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


class ManufacturingAdvisorAgent:
    """
    Manufacturing Advisor Agent.

    Enriches user queries with manufacturing domain knowledge.
    """

    def __init__(self):
        """Initialize the Manufacturing Advisor Agent."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info("Manufacturing Advisor Agent initialized")

    async def enrich_query(self, user_message: str, context: List[Dict[str, str]], session_id: str) -> Dict[str, Any]:
        """
        Enrich user query with manufacturing domain knowledge.
        Includes guardrails to reject out-of-scope questions.

        Args:
            user_message: User's natural language query
            context: Previous conversation messages
            session_id: Session identifier

        Returns:
            Enriched request dict with is_in_scope flag
        """
        # Build context string
        context_str = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in context[-3:]])

        # Use LLM to extract intent and entities with guardrails
        prompt = f"""You are a senior manufacturing engineer analyzing user queries for an automotive press analytics system.

GUARDRAILS - REJECT these out-of-scope queries:
- Questions about unrelated topics (weather, sports, general knowledge, etc.)
- Requests to perform actions outside analytics (send emails, create files, etc.)
- Personal questions or conversations unrelated to manufacturing
- Requests for data/systems we don't have access to

IN-SCOPE queries include:
- Questions about manufacturing data, metrics, processes
- Requests to analyze press operations, quality, defects, costs
- Questions about system capabilities and available data
- Comparisons, trends, root cause analysis
- Help with understanding the system
- Data exploration queries (latest records, time ranges, machine counts, etc.)
- Metadata queries (what data exists, date ranges, entity counts)

Manufacturing System Context:
- 2 Press Lines: LINE_A (800T, produces Door_Outer_Left and Door_Outer_Right), LINE_B (1200T, produces Bonnet_Outer)
- 3 Part Families: Door_Outer_Left, Door_Outer_Right, Bonnet_Outer

**Cube Selection Guide (IMPORTANT - select based on requested dimensions):**
- **PressOperations**: shift_id, operator_id, die_id, defect_type, defect_severity, quality_status, coil_id, is_weekend
- **PartFamilyPerformance**: part_family, part_type, material_grade (NO shift_id or operator_id)
- **PressLineUtilization**: press_line_id, line_name, part_type (NO shift_id or operator_id)

Previous Context:
{context_str}

User Query: "{user_message}"

IMPORTANT: Extract ONLY what the user explicitly asks for. Don't add extra metrics or dimensions.

Respond in JSON format:
{{
    "is_in_scope": true or false,
    "rejection_reason": "if out of scope, brief explanation",
    "user_intent": "brief description of what user wants",
    "part_families": ["ONLY part families explicitly mentioned by user"],
    "metrics": ["ONLY metrics explicitly requested by user"],
    "dimensions": ["ONLY dimensions explicitly requested for breakdown"],
    "cube_recommendation": "PressOperations|PartFamilyPerformance|PressLineUtilization",
    "filters": {{"filter_key": "filter_value"}}
}}

Examples:
- "What data do you have?" → in_scope: true, metrics: [], dimensions: [], cube_recommendation: "PressOperations"
- "Compare quality rates across shifts" → in_scope: true, metrics: ["pass_rate"], dimensions: ["shift_id"], cube_recommendation: "PressOperations"
- "Show me OEE by line" → in_scope: true, metrics: ["avgOee"], dimensions: ["press_line_id"], cube_recommendation: "PressLineUtilization"
- "Defects by operator" → in_scope: true, metrics: ["defect_count"], dimensions: ["operator_id"], cube_recommendation: "PressOperations"
- "Part family performance" → in_scope: true, metrics: ["pass_rate"], dimensions: ["part_family"], cube_recommendation: "PartFamilyPerformance"
- "What's the weather?" → in_scope: false, rejection_reason: "Weather data not available"
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            enriched = json.loads(response.choices[0].message.content)
            logger.info(f"Enriched query: {enriched}")

            return enriched

        except Exception as e:
            logger.error(f"Error enriching query: {e}")
            # Fallback: assume in-scope data query
            return {
                "is_in_scope": True,
                "rejection_reason": "",
                "user_intent": "general_query",
                "part_families": [],
                "metrics": ["count"],
                "dimensions": [],
                "cube_recommendation": "PressOperations",
                "filters": {},
            }



# Praval agent decorator
@agent(
    "manufacturing_advisor",
    responds_to=["user_query"],
    system_message="You are a senior manufacturing engineer with 20+ years in automotive stamping operations. You understand OEE, SMED, tonnage, springback, and all manufacturing terminology.",
    auto_broadcast=False
)
def manufacturing_advisor_handler(spore: Spore):
    """
    Handle user queries and enrich with manufacturing domain knowledge.

    Args:
        spore: Spore with user_query knowledge
    """
    import asyncio

    logger.info(f"Manufacturing Advisor received spore: {spore.id}")

    # Extract knowledge from spore
    knowledge = spore.knowledge
    user_message = knowledge.get("message", "")
    session_id = knowledge.get("session_id", "")
    context = knowledge.get("context", [])

    logger.info(f"Processing user query (session {session_id}): {user_message}")

    # Initialize advisor
    advisor = ManufacturingAdvisorAgent()

    # Enrich query with domain knowledge (unified flow for ALL queries)
    enriched = asyncio.run(advisor.enrich_query(user_message, context, session_id))

    # Check guardrails - reject out-of-scope queries
    if not enriched.get("is_in_scope", True):
        rejection_reason = enriched.get("rejection_reason", "This question is outside the scope of manufacturing analytics.")
        logger.info(f"Query rejected: {rejection_reason}")

        # Broadcast rejection as domain_enriched_request with special flag
        broadcast({
            "type": "domain_enriched_request",
            "is_rejected": True,
            "rejection_reason": rejection_reason,
            "session_id": session_id,
            "user_message": user_message,
        })
        return

    # Check if this is a metadata/capability question (no metrics, no dimensions)
    is_metadata_query = (
        not enriched.get("metrics") and
        not enriched.get("dimensions") and
        not enriched.get("part_families") and
        ("data" in user_message.lower() or "access" in user_message.lower() or "available" in user_message.lower() or "capability" in user_message.lower())
    )

    if is_metadata_query:
        logger.info(f"Detected metadata query - fetching Cube.js metadata")

        # Fetch metadata from Cube.js
        from cubejs_client import cubejs_client
        import asyncio
        try:
            metadata = asyncio.run(cubejs_client.get_meta())
            cubes = metadata.get("cubes", [])

            # Build response from actual Cube.js schema
            response_lines = ["**Available Data Sources:**\n"]

            for cube in cubes:
                cube_name = cube.get("name", "")
                title = cube.get("title", cube_name)

                response_lines.append(f"\n📊 **{cube_name}** - {title}")

                # List measures
                measures = cube.get("measures", [])
                if measures:
                    response_lines.append(f"   **Metrics ({len(measures)}):**")
                    for m in measures[:8]:  # Show first 8
                        m_title = m.get("title", m.get("name", ""))
                        response_lines.append(f"   • {m_title}")
                    if len(measures) > 8:
                        response_lines.append(f"   • ...and {len(measures) - 8} more")

                # List dimensions
                dimensions = cube.get("dimensions", [])
                if dimensions:
                    response_lines.append(f"   **Dimensions ({len(dimensions)}):**")
                    for d in dimensions[:8]:  # Show first 8
                        d_title = d.get("title", d.get("name", ""))
                        response_lines.append(f"   • {d_title}")
                    if len(dimensions) > 8:
                        response_lines.append(f"   • ...and {len(dimensions) - 8} more")

            response_lines.append(f"\n📅 **Data Coverage:** 4,320+ production records from 2 press lines\n")
            response_lines.append("\nYou can ask about production metrics, quality analysis, defect patterns, cost trends, and more.")

            capability_response = "\n".join(response_lines)

        except Exception as e:
            logger.error(f"Failed to fetch Cube.js metadata: {e}")
            # Fallback response
            capability_response = """**Available Data Sources:**

📊 **PressOperations** - Detailed press operation records
📈 **PartFamilyPerformance** - Aggregated part family metrics
🏭 **PressLineUtilization** - Press line efficiency data

Ask me about OEE, quality metrics, defects, costs, or production trends."""

        # Broadcast a direct response
        broadcast({
            "type": "final_response_ready",
            "narrative": capability_response,
            "chart_spec": None,
            "follow_ups": [
                "Show me OEE by press line",
                "What are the defect counts by part family?",
                "Compare quality rates across shifts"
            ],
            "session_id": session_id,
        })
        return

    # Build domain_enriched_request for ALL in-scope queries
    domain_enriched = {
        "type": "domain_enriched_request",
        "user_intent": enriched.get("user_intent", "general_query"),
        "part_families": enriched.get("part_families", []),
        "metrics": enriched.get("metrics", []),
        "dimensions": enriched.get("dimensions", []),
        "cube_recommendation": enriched.get("cube_recommendation", "PressOperations"),
        "filters": enriched.get("filters", {}),
        "time_range": None,
        "session_id": session_id,
        "user_message": user_message,
        "is_rejected": False,
    }

    logger.info(f"Broadcasting domain_enriched_request: intent={domain_enriched['user_intent']}")
    broadcast(domain_enriched)

    return
