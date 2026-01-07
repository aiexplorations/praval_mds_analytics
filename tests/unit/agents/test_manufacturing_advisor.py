"""Unit tests for Manufacturing Advisor Agent."""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from manufacturing_advisor import ManufacturingAdvisorAgent


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_in_scope_data_query():
    """Test enriching an in-scope data query."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "compare_quality_by_shift",
        "part_families": [],
        "metrics": ["pass_rate"],
        "dimensions": ["shift_id"],
        "cube_recommendation": "PressOperations",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "Compare quality rates across shifts",
            [],
            "test-session-123"
        )

    assert result["is_in_scope"] is True
    assert result["user_intent"] == "compare_quality_by_shift"
    assert "pass_rate" in result["metrics"]
    assert "shift_id" in result["dimensions"]
    assert result["cube_recommendation"] == "PressOperations"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_out_of_scope():
    """Test rejection of out-of-scope query."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": False,
        "rejection_reason": "Weather data not available in manufacturing analytics system",
        "user_intent": "",
        "part_families": [],
        "metrics": [],
        "dimensions": [],
        "cube_recommendation": "",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "What's the weather today?",
            [],
            "test-session-123"
        )

    assert result["is_in_scope"] is False
    assert "Weather data not available" in result["rejection_reason"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_with_part_families():
    """Test enriching query with specific part families."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "analyze_defects_by_part",
        "part_families": ["Door_Outer_Left", "Door_Outer_Right"],
        "metrics": ["defect_count"],
        "dimensions": ["part_family"],
        "cube_recommendation": "PartFamilyPerformance",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "Show me defects for door parts",
            [],
            "test-session-123"
        )

    assert result["is_in_scope"] is True
    assert "Door_Outer_Left" in result["part_families"]
    assert "Door_Outer_Right" in result["part_families"]
    assert "defect_count" in result["metrics"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_with_filters():
    """Test enriching query with filters."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "filter_by_press_line",
        "part_families": [],
        "metrics": ["avgOee"],
        "dimensions": [],
        "cube_recommendation": "PressLineUtilization",
        "filters": {"press_line_id": "LINE_A"}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "Show me OEE for LINE_A",
            [],
            "test-session-123"
        )

    assert result["is_in_scope"] is True
    assert result["filters"]["press_line_id"] == "LINE_A"
    assert "avgOee" in result["metrics"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_with_context():
    """Test enriching query using conversation context."""
    advisor = ManufacturingAdvisorAgent()

    context = [
        {"role": "user", "content": "Show me door defects"},
        {"role": "assistant", "content": "Here are the door defects..."},
        {"role": "user", "content": "What about bonnet?"}
    ]

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "compare_bonnet_defects",
        "part_families": ["Bonnet_Outer"],
        "metrics": ["defect_count"],
        "dimensions": ["part_family"],
        "cube_recommendation": "PartFamilyPerformance",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "What about bonnet?",
            context,
            "test-session-123"
        )

    assert result["is_in_scope"] is True
    assert "Bonnet_Outer" in result["part_families"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_error_handling():
    """Test fallback behavior when LLM call fails."""
    advisor = ManufacturingAdvisorAgent()

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, side_effect=Exception("API Error")):
        result = await advisor.enrich_query(
            "Show me production data",
            [],
            "test-session-123"
        )

    # Should return fallback with is_in_scope=True
    assert result["is_in_scope"] is True
    assert result["user_intent"] == "general_query"
    assert "count" in result["metrics"]
    assert result["cube_recommendation"] == "PressOperations"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_cube_selection_press_operations():
    """Test cube selection for PressOperations (shift/operator dimensions)."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "defects_by_operator",
        "part_families": [],
        "metrics": ["defect_count"],
        "dimensions": ["operator_id"],
        "cube_recommendation": "PressOperations",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "Show defects by operator",
            [],
            "test-session-123"
        )

    assert result["cube_recommendation"] == "PressOperations"
    assert "operator_id" in result["dimensions"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_cube_selection_part_family():
    """Test cube selection for PartFamilyPerformance."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "part_family_analysis",
        "part_families": [],
        "metrics": ["first_pass_yield"],
        "dimensions": ["part_family"],
        "cube_recommendation": "PartFamilyPerformance",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "Compare first pass yield by part family",
            [],
            "test-session-123"
        )

    assert result["cube_recommendation"] == "PartFamilyPerformance"
    assert "part_family" in result["dimensions"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_cube_selection_line_utilization():
    """Test cube selection for PressLineUtilization."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "line_oee_comparison",
        "part_families": [],
        "metrics": ["avgOee"],
        "dimensions": ["press_line_id"],
        "cube_recommendation": "PressLineUtilization",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "Show OEE by press line",
            [],
            "test-session-123"
        )

    assert result["cube_recommendation"] == "PressLineUtilization"
    assert "avgOee" in result["metrics"]
    assert "press_line_id" in result["dimensions"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enrich_query_metadata_detection():
    """Test detection of metadata/capability queries."""
    advisor = ManufacturingAdvisorAgent()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "is_in_scope": True,
        "rejection_reason": "",
        "user_intent": "explore_capabilities",
        "part_families": [],
        "metrics": [],
        "dimensions": [],
        "cube_recommendation": "PressOperations",
        "filters": {}
    })

    with patch.object(advisor.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await advisor.enrich_query(
            "What data do you have access to?",
            [],
            "test-session-123"
        )

    assert result["is_in_scope"] is True
    assert result["metrics"] == []
    assert result["dimensions"] == []
