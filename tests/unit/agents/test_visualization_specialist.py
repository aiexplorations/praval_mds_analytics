"""Unit tests for Visualization Specialist Agent."""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from visualization_specialist import VisualizationSpecialistAgent


@pytest.mark.unit
@pytest.mark.asyncio
async def test_determine_chart_type_kpi():
    """Test chart type selection for single value (KPI)."""
    agent = VisualizationSpecialistAgent()

    data = [{"PressOperations.avgOee": "85.5"}]
    measures = ["PressOperations.avgOee"]
    dimensions = []
    metadata = {"row_count": 1, "column_count": 1, "has_time_series": False}

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "chart_type": "kpi",
        "reasoning": "Single aggregate value best shown as KPI card"
    })

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        chart_type = await agent.determine_chart_type(data, measures, dimensions, metadata)

    assert chart_type == "kpi"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_determine_chart_type_bar():
    """Test chart type selection for categorical comparison (bar)."""
    agent = VisualizationSpecialistAgent()

    data = [
        {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.defectCount": "25"},
        {"PressOperations.partFamily": "Door_Outer_Right", "PressOperations.defectCount": "18"},
        {"PressOperations.partFamily": "Bonnet_Outer", "PressOperations.defectCount": "12"}
    ]
    measures = ["PressOperations.defectCount"]
    dimensions = ["PressOperations.partFamily"]
    metadata = {"row_count": 3, "column_count": 2, "has_time_series": False}

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "chart_type": "bar",
        "reasoning": "Comparing defects across part families"
    })

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        chart_type = await agent.determine_chart_type(data, measures, dimensions, metadata)

    assert chart_type == "bar"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_determine_chart_type_grouped_bar():
    """Test chart type selection for multi-dimensional comparison."""
    agent = VisualizationSpecialistAgent()

    data = [
        {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.defectType": "springback", "PressOperations.defectCount": "10"},
        {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.defectType": "wrinkle", "PressOperations.defectCount": "5"}
    ]
    measures = ["PressOperations.defectCount"]
    dimensions = ["PressOperations.partFamily", "PressOperations.defectType"]
    metadata = {"row_count": 2, "column_count": 3, "has_multiple_dimensions": True}

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "chart_type": "grouped_bar",
        "reasoning": "Multi-dimensional comparison with 2 dimensions"
    })

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        chart_type = await agent.determine_chart_type(data, measures, dimensions, metadata)

    assert chart_type == "grouped_bar"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_determine_chart_type_table():
    """Test chart type selection for large dataset (table)."""
    agent = VisualizationSpecialistAgent()

    data = [{"PressOperations.operatorId": f"OP_{i}", "PressOperations.defectCount": f"{i*10}"} for i in range(20)]
    measures = ["PressOperations.defectCount"]
    dimensions = ["PressOperations.operatorId"]
    metadata = {"row_count": 20, "column_count": 2}

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "chart_type": "table",
        "reasoning": "Large dataset with 20+ rows best shown as table"
    })

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        chart_type = await agent.determine_chart_type(data, measures, dimensions, metadata)

    assert chart_type == "table"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_determine_chart_type_empty_data():
    """Test chart type selection for empty data."""
    agent = VisualizationSpecialistAgent()

    data = []
    measures = ["PressOperations.count"]
    dimensions = []
    metadata = {"row_count": 0, "column_count": 0}

    chart_type = await agent.determine_chart_type(data, measures, dimensions, metadata)

    assert chart_type == "empty"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_determine_chart_type_fallback_on_error():
    """Test fallback behavior when LLM call fails."""
    agent = VisualizationSpecialistAgent()

    data = [{"value": "100"}]
    measures = ["measure"]
    dimensions = []
    metadata = {"row_count": 1, "column_count": 1}

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, side_effect=Exception("API Error")):
        chart_type = await agent.determine_chart_type(data, measures, dimensions, metadata)

    # Should fallback to heuristic: 1 row = kpi
    assert chart_type == "kpi"


@pytest.mark.unit
def test_generate_chart_spec_empty():
    """Test chart spec generation for empty data."""
    agent = VisualizationSpecialistAgent()

    spec = agent.generate_chart_spec([], [], [], "empty", {})

    assert spec["type"] == "empty"
    assert "No data available" in spec["message"]


@pytest.mark.unit
def test_generate_chart_spec_table():
    """Test table generation for multiple rows."""
    agent = VisualizationSpecialistAgent()

    data = [
        {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.count": "100"},
        {"PressOperations.partFamily": "Door_Outer_Right", "PressOperations.count": "95"}
    ]
    measures = ["PressOperations.count"]
    dimensions = ["PressOperations.partFamily"]
    metadata = {"row_count": 2}

    spec = agent.generate_chart_spec(data, measures, dimensions, "table", metadata)

    assert spec["type"] == "table"
    # Table should have columns and rows structure
    assert "columns" in spec or "rows" in spec or "data" in spec
