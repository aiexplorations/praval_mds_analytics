"""Tests for FastAPI endpoints."""
import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from app import app
from models import CubeQuery, ChartData
import report_writer


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint."""
    with patch("cubejs_client.cubejs_client.health_check", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = True

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["cubejs_connected"] is True


def test_chat_endpoint_invalid_request():
    """Test chat endpoint with invalid request."""
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Validation error


def test_chat_endpoint_creates_session():
    """Test that chat endpoint creates a session if none provided.

    The Praval multi-agent system handles user queries via Manufacturing Advisor,
    Analytics Specialist, and Report Writer agents. For non-data queries like
    'Hello', the system guides users toward manufacturing analytics questions.
    """
    # Mock the report_writer._pending_responses to provide a test response
    with patch.object(report_writer, '_pending_responses', {}) as mock_responses:
        # Pre-populate response for any session (we don't know the ID yet)
        # The endpoint will create a session and look for a response

        # We need to mock the response after the session is created
        # Use a side effect to capture the session_id and inject response
        original_broadcast = None
        captured_session_id = None

        def capture_and_respond(from_agent, knowledge):
            nonlocal captured_session_id
            if knowledge.get("type") == "user_query":
                captured_session_id = knowledge.get("session_id")
                # Inject a mock response for this session
                mock_responses[captured_session_id] = {
                    "narrative": "Hello! I can help you analyze automotive press manufacturing data.",
                    "chart_spec": None,
                    "follow_ups": ["What's the OEE?", "Show me quality trends"]
                }

        with patch("app.get_reef") as mock_get_reef:
            mock_reef = mock_get_reef.return_value
            mock_reef.broadcast.side_effect = capture_and_respond
            mock_reef.get_network_stats.return_value = {"channel_stats": {}}

            response = client.post("/chat", json={"message": "Hello"})

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        # Verify a message was returned (content may vary based on agent responses)
        assert "message" in data
        assert len(data["message"]) > 0


@pytest.mark.asyncio
async def test_chat_endpoint_with_data_query():
    """Test chat endpoint with a data query."""
    with patch("chat_agent.chat_agent.should_query_data", new_callable=AsyncMock) as mock_should_query, \
         patch("data_analyst_agent.data_analyst_agent.translate_to_query", new_callable=AsyncMock) as mock_translate, \
         patch("cubejs_client.cubejs_client.execute_query", new_callable=AsyncMock) as mock_execute, \
         patch("data_analyst_agent.data_analyst_agent.generate_insights", new_callable=AsyncMock) as mock_insights:

        mock_should_query.return_value = True
        mock_translate.return_value = (
            CubeQuery(measures=["ProductionQuality.passRate"], dimensions=["ProductionQuality.componentType"]),
            "bar"
        )
        mock_execute.return_value = {
            "data": [
                {"ProductionQuality.componentType": "refills", "ProductionQuality.passRate": "95"}
            ]
        }
        mock_insights.return_value = ["Refills have 95% pass rate"]

        response = client.post("/chat", json={"message": "What's the pass rate?"})

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "chart" in data
        assert "insights" in data


def test_get_session_not_found():
    """Test getting a non-existent session."""
    response = client.get("/session/non-existent-id")
    assert response.status_code == 404


def test_delete_session():
    """Test deleting a session."""
    # First create a session via chat
    with patch("chat_agent.chat_agent.should_query_data", new_callable=AsyncMock) as mock_should_query, \
         patch("chat_agent.chat_agent.generate_conversational_response", new_callable=AsyncMock) as mock_response:

        mock_should_query.return_value = False
        mock_response.return_value = "Hello!"

        create_response = client.post("/chat", json={"message": "Hi"})
        session_id = create_response.json()["session_id"]

        # Delete the session
        delete_response = client.delete(f"/session/{session_id}")
        assert delete_response.status_code == 200

        # Verify it's gone
        get_response = client.get(f"/session/{session_id}")
        assert get_response.status_code == 404


def test_agents_endpoint():
    """Test agents listing endpoint."""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "agents" in data
    assert "total_count" in data
    assert isinstance(data["agents"], list)
    assert data["total_count"] == len(data["agents"])

    # Should have at least the 5 main agents
    # (manufacturing_advisor, analytics_specialist, visualization_specialist,
    #  quality_inspector, report_writer)
    assert data["total_count"] >= 5


def test_agents_endpoint_returns_valid_agent_info():
    """Test that agents endpoint returns valid agent information."""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()

    agents = data["agents"]
    assert len(agents) > 0

    # Check first agent has required fields
    agent = agents[0]
    assert "name" in agent
    assert "status" in agent
    assert "description" in agent
    assert "provider" in agent or agent.get("provider") is None
    assert "tools" in agent
    assert "memory_enabled" in agent

    # Verify field types
    assert isinstance(agent["name"], str)
    assert agent["status"] in ["active", "inactive"]
    assert isinstance(agent["description"], str)
    assert isinstance(agent["tools"], list)
    assert isinstance(agent["memory_enabled"], bool)


def test_agents_endpoint_includes_expected_agents():
    """Test that the expected Praval agents are included."""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()

    agent_names = [agent["name"] for agent in data["agents"]]

    # Expected agents from the Praval architecture
    expected_agents = [
        "manufacturing_advisor",
        "analytics_specialist",
        "visualization_specialist",
        "quality_inspector",
        "report_writer"
    ]

    # All expected agents should be present
    for expected_agent in expected_agents:
        assert expected_agent in agent_names, f"Expected agent '{expected_agent}' not found in agent list"
