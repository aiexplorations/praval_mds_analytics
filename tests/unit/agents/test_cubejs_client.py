"""Unit tests for Cube.js Client."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from cubejs_client import CubeJSClient
from models import CubeQuery


@pytest.mark.unit
def test_cubejs_client_initialization():
    """Test Cube.js client initialization."""
    client = CubeJSClient(
        api_url="http://localhost:4000/cubejs-api/v1",
        api_secret="test-secret"
    )

    assert client.api_url == "http://localhost:4000/cubejs-api/v1"
    assert client.api_secret == "test-secret"
    assert client.headers["Authorization"] == "test-secret"
    assert client.headers["Content-Type"] == "application/json"


@pytest.mark.unit
def test_cubejs_client_uses_settings_defaults():
    """Test that client uses settings when no params provided."""
    with patch('cubejs_client.settings') as mock_settings:
        mock_settings.cubejs_api_url = "http://cubejs:4000/cubejs-api/v1"
        mock_settings.cubejs_api_secret = "mysecretkey"

        client = CubeJSClient()

        assert client.api_url == "http://cubejs:4000/cubejs-api/v1"
        assert client.api_secret == "mysecretkey"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_query_success():
    """Test successful query execution."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.count"],
        dimensions=["PressOperations.partFamily"]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"PressOperations.partFamily": "Door_Outer_Left", "PressOperations.count": "100"}
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert result["data"][0]["PressOperations.count"] == "100"
    mock_client.post.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_query_http_error():
    """Test query execution with HTTP error."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.invalidMeasure"]
    )

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Invalid measure"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request",
        request=MagicMock(),
        response=mock_response
    )

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        with pytest.raises(ValueError, match="Cube.js query failed"):
            await client.execute_query(query)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_execute_query_connection_error():
    """Test query execution with connection error."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.count"]
    )

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.RequestError("Connection refused")
        mock_httpx.return_value.__aenter__.return_value = mock_client

        with pytest.raises(ConnectionError, match="Cannot connect to Cube.js"):
            await client.execute_query(query)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_meta_success():
    """Test successful metadata retrieval."""
    client = CubeJSClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cubes": [
            {
                "name": "PressOperations",
                "measures": [{"name": "count"}],
                "dimensions": [{"name": "partFamily"}]
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.get_meta()

    assert "cubes" in result
    assert result["cubes"][0]["name"] == "PressOperations"
    mock_client.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_healthy():
    """Test health check when Cube.js is accessible."""
    client = CubeJSClient()

    with patch.object(client, 'get_meta', new_callable=AsyncMock, return_value={"cubes": []}):
        result = await client.health_check()

    assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_unhealthy():
    """Test health check when Cube.js is not accessible."""
    client = CubeJSClient()

    with patch.object(client, 'get_meta', new_callable=AsyncMock, side_effect=Exception("Connection error")):
        result = await client.health_check()

    assert result is False
