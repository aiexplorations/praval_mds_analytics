"""Integration tests for multi-agent collaboration."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import json

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from manufacturing_advisor import ManufacturingAdvisorAgent
from analytics_specialist import AnalyticsSpecialistAgent
from visualization_specialist import VisualizationSpecialistAgent
from quality_inspector import QualityInspectorAgent
from models import CubeQuery


@pytest.mark.integration
@pytest.mark.asyncio
async def test_manufacturing_advisor_to_analytics_specialist():
    """Test Manufacturing Advisor enriching query for Analytics Specialist."""
    # Initialize agents
    advisor = ManufacturingAdvisorAgent()
    specialist = AnalyticsSpecialistAgent()

    # Mock LLM response for advisor
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "compare_defects_by_part_family",
        "part_families": ["Door_Outer_Left", "Door_Outer_Right"],
        "metrics": ["defect_count"],
        "dimensions": ["part_family"],
        "cube_recommendation": "PartFamilyPerformance",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_llm_response):
        # Step 1: Advisor enriches the query
        enriched = await advisor.enrich_query(
            "Compare defects for door parts",
            [],
            "test-session-123"
        )

    # Step 2: Specialist builds query from enriched request
    query = specialist.build_cube_query(enriched)

    # Verify collaboration
    assert enriched["is_in_scope"] is True
    assert enriched["cube_recommendation"] == "PartFamilyPerformance"
    assert "defect_count" in enriched["metrics"]
    assert "PartFamilyPerformance" in query.measures[0]
    assert query.filters is not None
    assert len(query.filters) == 1  # Part family filter


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analytics_specialist_to_visualization_specialist():
    """Test Analytics Specialist providing data to Visualization Specialist."""
    # Initialize agents
    specialist = AnalyticsSpecialistAgent()
    viz_agent = VisualizationSpecialistAgent()

    # Mock Cube.js response
    mock_result = {
        "data": [
            {"PartFamilyPerformance.partFamily": "Door_Outer_Left", "PartFamilyPerformance.defectCount": "45"},
            {"PartFamilyPerformance.partFamily": "Door_Outer_Right", "PartFamilyPerformance.defectCount": "28"}
        ]
    }

    query = CubeQuery(
        measures=["PartFamilyPerformance.defectCount"],
        dimensions=["PartFamilyPerformance.partFamily"]
    )

    with patch.object(specialist.client, 'execute_query', new_callable=AsyncMock, return_value=mock_result):
        # Step 1: Specialist executes query
        data_ready = await specialist.execute_query(query, "test-session-123")

    # Mock LLM for chart type selection
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message.content = json.dumps({
        "chart_type": "bar",
        "reasoning": "Comparing defects across 2 part families"
    })

    with patch.object(viz_agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_llm_response):
        # Step 2: Viz agent determines chart type
        chart_type = await viz_agent.determine_chart_type(
            data_ready["query_results"],
            data_ready["measures"],
            data_ready["dimensions"],
            data_ready["metadata"]
        )

    # Verify collaboration
    assert data_ready["row_count"] == 2
    assert chart_type == "bar"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_analytics_specialist_to_quality_inspector():
    """Test Analytics Specialist providing data to Quality Inspector."""
    # Initialize agents
    specialist = AnalyticsSpecialistAgent()
    inspector = QualityInspectorAgent()

    # Mock Cube.js response with quality data
    mock_result = {
        "data": [
            {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.passRate": "89.5"},
            {"PressOperations.partFamily": "Door_Outer_Right", "PressOperations.passRate": "95.8"},
            {"PressOperations.partFamily": "Bonnet_Outer", "PressOperations.passRate": "97.2"}
        ]
    }

    query = CubeQuery(
        measures=["PressOperations.passRate"],
        dimensions=["PressOperations.partFamily"]
    )

    with patch.object(specialist.client, 'execute_query', new_callable=AsyncMock, return_value=mock_result):
        # Step 1: Specialist executes query
        data_ready = await specialist.execute_query(query, "test-session-123")

    # Mock LLM for quality analysis
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message.content = json.dumps({
        "observations": [
            {
                "type": "comparative",
                "text": "Door_Outer_Left has lowest pass rate at 89.5%",
                "confidence": 0.9,
                "data_points": {"lowest": 89.5, "highest": 97.2}
            }
        ],
        "anomalies": [
            {
                "entity": "Door_Outer_Left",
                "metric": "pass_rate",
                "value": 89.5,
                "severity": "medium",
                "description": "Pass rate below 90% threshold"
            }
        ],
        "root_causes": [
            {
                "hypothesis": "Die wear or material issues on LINE_A",
                "confidence": 0.7,
                "supporting_evidence": ["Lowest quality among all parts"]
            }
        ]
    })

    with patch.object(inspector.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_llm_response):
        # Step 2: Inspector analyzes data
        insights = await inspector.analyze_data(
            data_ready["query_results"],
            data_ready["measures"],
            data_ready["dimensions"],
            data_ready["cube_used"],
            "test-session-123"
        )

    # Verify collaboration
    assert insights["type"] == "insights_ready"
    assert len(insights["observations"]) == 1
    assert len(insights["anomalies"]) == 1
    assert len(insights["root_causes"]) == 1
    assert insights["observations"][0]["type"] == "comparative"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_agent_pipeline_data_query():
    """Test complete pipeline: Advisor → Specialist → Viz + Quality."""
    # Initialize all agents
    advisor = ManufacturingAdvisorAgent()
    specialist = AnalyticsSpecialistAgent()
    viz_agent = VisualizationSpecialistAgent()
    inspector = QualityInspectorAgent()

    # Step 1: Advisor enriches query
    mock_advisor_llm = MagicMock()
    mock_advisor_llm.choices = [MagicMock()]
    mock_advisor_llm.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "analyze_oee_by_line",
        "part_families": [],
        "metrics": ["avgOee"],
        "dimensions": ["press_line_id"],
        "cube_recommendation": "PressLineUtilization",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_advisor_llm):
        enriched = await advisor.enrich_query(
            "Show me OEE by press line",
            [],
            "test-session-123"
        )

    # Step 2: Specialist builds and executes query
    query = specialist.build_cube_query(enriched)

    mock_cube_result = {
        "data": [
            {"PressLineUtilization.pressLineId": "LINE_A", "PressLineUtilization.overallAvgOee": "82.5"},
            {"PressLineUtilization.pressLineId": "LINE_B", "PressLineUtilization.overallAvgOee": "87.3"}
        ]
    }

    with patch.object(specialist.client, 'execute_query', new_callable=AsyncMock, return_value=mock_cube_result):
        data_ready = await specialist.execute_query(query, "test-session-123")

    # Step 3a: Viz agent selects chart type
    mock_viz_llm = MagicMock()
    mock_viz_llm.choices = [MagicMock()]
    mock_viz_llm.choices[0].message.content = json.dumps({
        "chart_type": "bar",
        "reasoning": "Comparing OEE across 2 press lines"
    })

    with patch.object(viz_agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_viz_llm):
        chart_type = await viz_agent.determine_chart_type(
            data_ready["query_results"],
            data_ready["measures"],
            data_ready["dimensions"],
            data_ready["metadata"]
        )

    # Step 3b: Inspector analyzes data (parallel to viz)
    mock_inspector_llm = MagicMock()
    mock_inspector_llm.choices = [MagicMock()]
    mock_inspector_llm.choices[0].message.content = json.dumps({
        "observations": [
            {
                "type": "comparative",
                "text": "LINE_B achieves 5.8% higher OEE than LINE_A",
                "confidence": 0.95,
                "data_points": {"LINE_A": 82.5, "LINE_B": 87.3}
            }
        ],
        "anomalies": [],
        "root_causes": []
    })

    with patch.object(inspector.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_inspector_llm):
        insights = await inspector.analyze_data(
            data_ready["query_results"],
            data_ready["measures"],
            data_ready["dimensions"],
            data_ready["cube_used"],
            "test-session-123"
        )

    # Verify full pipeline
    assert enriched["is_in_scope"] is True
    assert enriched["cube_recommendation"] == "PressLineUtilization"
    assert "PressLineUtilization.overallAvgOee" in query.measures
    assert data_ready["row_count"] == 2
    assert chart_type == "bar"
    assert len(insights["observations"]) == 1
    assert insights["session_id"] == "test-session-123"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_out_of_scope_query_rejection():
    """Test that out-of-scope queries are rejected early in pipeline."""
    advisor = ManufacturingAdvisorAgent()

    # Mock LLM rejection
    mock_llm_response = MagicMock()
    mock_llm_response.choices = [MagicMock()]
    mock_llm_response.choices[0].message.content = json.dumps({
        "is_in_scope": False,
        "rejection_reason": "Weather data is not available in manufacturing analytics system",
        "user_intent": "",
        "part_families": [],
        "metrics": [],
        "dimensions": [],
        "cube_recommendation": "",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_llm_response):
        enriched = await advisor.enrich_query(
            "What's the weather forecast?",
            [],
            "test-session-123"
        )

    # Verify rejection stops the pipeline
    assert enriched["is_in_scope"] is False
    assert "Weather data" in enriched["rejection_reason"]
    # Pipeline should not continue to Analytics Specialist


@pytest.mark.integration
@pytest.mark.asyncio
async def test_empty_result_handling():
    """Test how agents handle empty query results."""
    specialist = AnalyticsSpecialistAgent()
    viz_agent = VisualizationSpecialistAgent()
    inspector = QualityInspectorAgent()

    # Mock empty Cube.js response
    mock_result = {"data": []}

    query = CubeQuery(
        measures=["PressOperations.count"],
        dimensions=["PressOperations.partFamily"],
        filters=[{"member": "PressOperations.partFamily", "operator": "equals", "values": ["NonExistent_Part"]}]
    )

    with patch.object(specialist.client, 'execute_query', new_callable=AsyncMock, return_value=mock_result):
        data_ready = await specialist.execute_query(query, "test-session-123")

    # Viz agent should handle empty data
    chart_type = await viz_agent.determine_chart_type(
        data_ready["query_results"],
        data_ready["measures"],
        data_ready["dimensions"],
        data_ready["metadata"]
    )

    # Inspector should handle empty data
    insights = await inspector.analyze_data(
        data_ready["query_results"],
        data_ready["measures"],
        data_ready["dimensions"],
        data_ready["cube_used"],
        "test-session-123"
    )

    # Verify graceful handling
    assert data_ready["row_count"] == 0
    assert chart_type == "empty"
    assert insights["observations"] == []
    assert insights["anomalies"] == []
