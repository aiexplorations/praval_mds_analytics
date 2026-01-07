"""Unit tests for Analytics Specialist Agent."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from analytics_specialist import AnalyticsSpecialistAgent, METRIC_MAPPING, DIMENSION_MAPPING
from models import CubeQuery


@pytest.mark.unit
def test_build_cube_query_press_operations():
    """Test building query for PressOperations cube."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressOperations",
        "metrics": ["pass_rate", "defect_count"],
        "dimensions": ["shift_id", "operator_id"],
        "part_families": [],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    assert "PressOperations.passRate" in query.measures
    assert "PressOperations.defectCount" in query.measures
    assert "PressOperations.shiftId" in query.dimensions
    assert "PressOperations.operatorId" in query.dimensions


@pytest.mark.unit
def test_build_cube_query_part_family_performance():
    """Test building query for PartFamilyPerformance cube."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PartFamilyPerformance",
        "metrics": ["first_pass_yield", "total_parts"],
        "dimensions": ["part_family"],
        "part_families": [],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    assert "PartFamilyPerformance.firstPassYield" in query.measures
    assert "PartFamilyPerformance.totalPartsProduced" in query.measures
    assert "PartFamilyPerformance.partFamily" in query.dimensions


@pytest.mark.unit
def test_build_cube_query_press_line_utilization():
    """Test building query for PressLineUtilization cube."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressLineUtilization",
        "metrics": ["avgOee", "utilization_rate"],
        "dimensions": ["press_line_id"],
        "part_families": [],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    assert "PressLineUtilization.overallAvgOee" in query.measures
    assert "PressLineUtilization.utilizationRate" in query.measures
    assert "PressLineUtilization.pressLineId" in query.dimensions


@pytest.mark.unit
def test_build_cube_query_with_part_family_filter():
    """Test building query with part family filters."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PartFamilyPerformance",
        "metrics": ["total_parts"],
        "dimensions": ["part_family"],
        "part_families": ["Door_Outer_Left", "Door_Outer_Right"],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    assert query.filters is not None
    assert len(query.filters) == 1
    assert query.filters[0]["member"] == "PartFamilyPerformance.partFamily"
    assert "Door_Outer_Left" in query.filters[0]["values"]
    assert "Door_Outer_Right" in query.filters[0]["values"]


@pytest.mark.unit
def test_build_cube_query_with_custom_filters():
    """Test building query with custom filters."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressOperations",
        "metrics": ["avgOee"],
        "dimensions": [],
        "part_families": [],
        "filters": {"press_line_id": "LINE_A", "shift_id": ["SHIFT_1", "SHIFT_2"]},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    assert query.filters is not None
    assert len(query.filters) == 2


@pytest.mark.unit
def test_build_cube_query_with_time_range():
    """Test building query with time range filter."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressOperations",
        "metrics": ["count"],
        "dimensions": [],
        "part_families": [],
        "filters": {},
        "time_range": {"start": "2024-01-01", "end": "2024-01-31"}
    }

    query = agent.build_cube_query(enriched_request)

    assert query.timeDimensions is not None
    assert len(query.timeDimensions) == 1
    assert query.timeDimensions[0]["dimension"] == "PressOperations.productionDate"


@pytest.mark.unit
def test_build_cube_query_default_count_metric():
    """Test that default count metric is used when no metrics provided."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressOperations",
        "metrics": [],
        "dimensions": ["part_family"],
        "part_families": [],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    assert "PressOperations.count" in query.measures
    assert len(query.measures) == 1


@pytest.mark.unit
def test_build_cube_query_handles_unmapped_metrics():
    """Test that unmapped metrics are skipped gracefully."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressOperations",
        "metrics": ["invalid_metric", "pass_rate"],
        "dimensions": [],
        "part_families": [],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    # Should only include the valid metric
    assert "PressOperations.passRate" in query.measures
    assert len(query.measures) == 1


@pytest.mark.unit
def test_build_cube_query_handles_unmapped_dimensions():
    """Test that unmapped dimensions are skipped gracefully."""
    agent = AnalyticsSpecialistAgent()

    enriched_request = {
        "cube_recommendation": "PressOperations",
        "metrics": ["count"],
        "dimensions": ["invalid_dimension", "shift_id"],
        "part_families": [],
        "filters": {},
        "time_range": None
    }

    query = agent.build_cube_query(enriched_request)

    # Should only include the valid dimension
    assert "PressOperations.shiftId" in query.dimensions
    assert len(query.dimensions) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_query_success():
    """Test successful query execution."""
    agent = AnalyticsSpecialistAgent()

    query = CubeQuery(
        measures=["PressOperations.passRate"],
        dimensions=["PressOperations.partFamily"]
    )

    mock_result = {
        "data": [
            {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.passRate": "95.5"},
            {"PressOperations.partFamily": "Door_Outer_Right", "PressOperations.passRate": "94.2"}
        ]
    }

    with patch.object(agent.client, 'execute_query', new_callable=AsyncMock, return_value=mock_result):
        result = await agent.execute_query(query, "test-session-123")

    assert result["query_results"] == mock_result["data"]
    assert result["row_count"] == 2
    assert result["session_id"] == "test-session-123"
    assert "query_time_ms" in result or "execution_time_seconds" in result
