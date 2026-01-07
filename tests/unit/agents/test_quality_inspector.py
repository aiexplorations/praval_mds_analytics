"""Unit tests for Quality Inspector Agent."""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from quality_inspector import QualityInspectorAgent


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_data_with_observations():
    """Test data analysis with observations and insights."""
    agent = QualityInspectorAgent()

    data = [
        {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.defectCount": "45"},
        {"PressOperations.partFamily": "Door_Outer_Right", "PressOperations.defectCount": "12"},
        {"PressOperations.partFamily": "Bonnet_Outer", "PressOperations.defectCount": "8"}
    ]
    measures = ["PressOperations.defectCount"]
    dimensions = ["PressOperations.partFamily"]

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "observations": [
            {
                "type": "comparative",
                "text": "Door_Outer_Left has significantly higher defect count (45) compared to Door_Outer_Right (12)",
                "confidence": 0.9,
                "data_points": {"Door_Outer_Left_defects": 45, "Door_Outer_Right_defects": 12}
            }
        ],
        "anomalies": [
            {
                "entity": "Door_Outer_Left",
                "metric": "defect_count",
                "value": 45,
                "severity": "high",
                "description": "Defect count 3.75x higher than Door_Outer_Right"
            }
        ],
        "root_causes": [
            {
                "hypothesis": "Die wear on LINE_A tooling for left door panels",
                "confidence": 0.7,
                "supporting_evidence": ["High defect concentration in Door_Outer_Left"]
            }
        ]
    })

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await agent.analyze_data(data, measures, dimensions, "PressOperations", "test-session-123")

    assert result["type"] == "insights_ready"
    assert len(result["observations"]) == 1
    assert len(result["anomalies"]) == 1
    assert len(result["root_causes"]) == 1
    assert result["session_id"] == "test-session-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_data_empty_dataset():
    """Test analysis of empty dataset."""
    agent = QualityInspectorAgent()

    result = await agent.analyze_data([], [], [], "PressOperations", "test-session-123")

    assert result["type"] == "insights_ready"
    assert result["observations"] == []
    assert result["anomalies"] == []
    assert result["root_causes"] == []
    assert result["session_id"] == "test-session-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_data_quality_metrics():
    """Test analysis focused on quality metrics."""
    agent = QualityInspectorAgent()

    data = [
        {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.passRate": "92.5"},
        {"PressOperations.partFamily": "Door_Outer_Right", "PressOperations.passRate": "95.8"},
        {"PressOperations.partFamily": "Bonnet_Outer", "PressOperations.passRate": "97.2"}
    ]
    measures = ["PressOperations.passRate"]
    dimensions = ["PressOperations.partFamily"]

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "observations": [
            {
                "type": "pattern",
                "text": "Pass rates vary from 92.5% to 97.2%, with Door_Outer_Left showing lowest quality",
                "confidence": 0.95,
                "data_points": {"lowest": 92.5, "highest": 97.2}
            }
        ],
        "anomalies": [],
        "root_causes": [
            {
                "hypothesis": "Door_Outer_Left complexity or die condition affecting quality",
                "confidence": 0.6,
                "supporting_evidence": ["Lower pass rate compared to other parts"]
            }
        ]
    })

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
        result = await agent.analyze_data(data, measures, dimensions, "PressOperations", "test-session-123")

    assert len(result["observations"]) == 1
    assert result["observations"][0]["type"] == "pattern"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_data_error_handling():
    """Test fallback behavior when LLM call fails."""
    agent = QualityInspectorAgent()

    data = [{"metric": "100"}]
    measures = ["measure"]
    dimensions = []

    with patch.object(agent.client.chat.completions, 'create', new_callable=AsyncMock, side_effect=Exception("API Error")):
        result = await agent.analyze_data(data, measures, dimensions, "PressOperations", "test-session-123")

    # Should return empty insights on error
    assert result["type"] == "insights_ready"
    assert result["observations"] == []
    assert result["session_id"] == "test-session-123"
