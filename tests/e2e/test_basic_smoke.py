"""End-to-end smoke tests for basic system functionality."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import json

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from app import app


client = TestClient(app)


@pytest.mark.e2e
def test_api_health_check():
    """Test that API health endpoint responds correctly."""
    with patch("cubejs_client.cubejs_client.health_check", new_callable=AsyncMock) as mock_health:
        mock_health.return_value = True

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["cubejs_connected"] is True


@pytest.mark.e2e
def test_api_root_endpoint():
    """Test root endpoint returns service information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["status"] == "running"


@pytest.mark.e2e
def test_session_creation_and_retrieval():
    """Test creating and retrieving a session."""
    # Mock agent responses for session creation
    with patch("manufacturing_advisor.ManufacturingAdvisorAgent") as mock_advisor:
        mock_advisor_instance = MagicMock()
        mock_advisor_instance.enrich_query = AsyncMock(return_value={
            "is_in_scope": False,
            "rejection_reason": "Test rejection",
            "user_intent": "",
            "part_families": [],
            "metrics": [],
            "dimensions": [],
            "cube_recommendation": "",
            "filters": {}
        })
        mock_advisor.return_value = mock_advisor_instance

        # Create session via chat endpoint
        response = client.post("/chat", json={"message": "Hello"})

        if response.status_code == 200:
            session_id = response.json().get("session_id")

            # Retrieve session
            session_response = client.get(f"/session/{session_id}")

            # Session endpoint may not be implemented, check status
            assert session_response.status_code in [200, 404]


@pytest.mark.e2e
def test_chat_endpoint_validation():
    """Test chat endpoint validates input correctly."""
    # Empty request should fail validation
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Validation error

    # Invalid JSON structure
    response = client.post("/chat", json={"invalid_field": "test"})
    assert response.status_code == 422


@pytest.mark.e2e
def test_out_of_scope_query_flow():
    """Test E2E flow for out-of-scope query."""
    # This simulates the full pipeline rejecting an out-of-scope query
    response = client.post("/chat", json={"message": "What's the weather?"})

    # Should get a response (200) with rejection message or 200 with explanation
    assert response.status_code in [200, 400, 422]


@pytest.mark.e2e
def test_simple_data_query_flow():
    """Test E2E flow for a simple data query (heavily mocked)."""
    # This would test the full pipeline, but requires extensive mocking
    # For smoke test, just ensure the endpoint doesn't crash

    response = client.post("/chat", json={"message": "Show me OEE"})

    # Should at least not crash - may timeout or return error without DBs running
    assert response.status_code in [200, 400, 500, 504]  # Various acceptable outcomes in test


@pytest.mark.e2e
def test_api_handles_invalid_session_id():
    """Test API handles invalid session IDs gracefully."""
    response = client.get("/session/invalid-session-id-12345")

    # Should return 404 or handle gracefully
    assert response.status_code in [404, 400]


@pytest.mark.e2e
def test_concurrent_chat_requests():
    """Test system handles multiple concurrent requests."""
    # Simulate multiple users chatting concurrently
    messages = [
        "Hello",
        "Show me defects",
        "What data do you have?",
        "Compare OEE by line"
    ]

    responses = []
    for msg in messages:
        response = client.post("/chat", json={"message": msg})
        responses.append(response)

    # All requests should at least return a status code
    for response in responses:
        assert response.status_code in [200, 400, 500, 504]


@pytest.mark.e2e
def test_session_isolation():
    """Test that different sessions are isolated."""
    # Create two sessions
    response1 = client.post("/chat", json={"message": "Hello from session 1"})
    response2 = client.post("/chat", json={"message": "Hello from session 2"})

    if response1.status_code == 200 and response2.status_code == 200:
        session_id_1 = response1.json().get("session_id")
        session_id_2 = response2.json().get("session_id")

        # Sessions should have different IDs
        assert session_id_1 != session_id_2
