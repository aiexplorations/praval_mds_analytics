"""Integration tests for Cube.js schema validation and queries."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from cubejs_client import CubeJSClient
from models import CubeQuery


@pytest.mark.integration
@pytest.mark.asyncio
async def test_press_operations_cube_query():
    """Test querying PressOperations cube with typical measures and dimensions."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.count", "PressOperations.passRate"],
        dimensions=["PressOperations.partFamily"]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "PressOperations.partFamily": "Door_Outer_Left",
                "PressOperations.count": "1500",
                "PressOperations.passRate": "94.5"
            },
            {
                "PressOperations.partFamily": "Door_Outer_Right",
                "PressOperations.count": "1480",
                "PressOperations.passRate": "95.2"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert "data" in result
    assert len(result["data"]) == 2
    assert result["data"][0]["PressOperations.partFamily"] == "Door_Outer_Left"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_part_family_performance_cube_query():
    """Test querying PartFamilyPerformance cube."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PartFamilyPerformance.totalPartsProduced", "PartFamilyPerformance.firstPassYield"],
        dimensions=["PartFamilyPerformance.partFamily"]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "PartFamilyPerformance.partFamily": "Door_Outer_Left",
                "PartFamilyPerformance.totalPartsProduced": "1500",
                "PartFamilyPerformance.firstPassYield": "0.945"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert "data" in result
    assert result["data"][0]["PartFamilyPerformance.partFamily"] == "Door_Outer_Left"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_press_line_utilization_cube_query():
    """Test querying PressLineUtilization cube."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressLineUtilization.overallAvgOee", "PressLineUtilization.utilizationRate"],
        dimensions=["PressLineUtilization.pressLineId"]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "PressLineUtilization.pressLineId": "LINE_A",
                "PressLineUtilization.overallAvgOee": "0.825",
                "PressLineUtilization.utilizationRate": "0.88"
            },
            {
                "PressLineUtilization.pressLineId": "LINE_B",
                "PressLineUtilization.overallAvgOee": "0.873",
                "PressLineUtilization.utilizationRate": "0.92"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert len(result["data"]) == 2
    assert result["data"][0]["PressLineUtilization.pressLineId"] == "LINE_A"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_query_with_filters():
    """Test Cube.js query with filters."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.defectCount"],
        dimensions=["PressOperations.defectType"],
        filters=[
            {
                "member": "PressOperations.partFamily",
                "operator": "equals",
                "values": ["Door_Outer_Left"]
            }
        ]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"PressOperations.defectType": "springback", "PressOperations.defectCount": "15"},
            {"PressOperations.defectType": "wrinkle", "PressOperations.defectCount": "8"},
            {"PressOperations.defectType": "scratch", "PressOperations.defectCount": "12"}
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert len(result["data"]) == 3
    assert result["data"][0]["PressOperations.defectType"] == "springback"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_query_with_time_dimensions():
    """Test Cube.js query with time dimensions."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.count"],
        dimensions=[],
        timeDimensions=[
            {
                "dimension": "PressOperations.productionDate",
                "dateRange": ["2024-01-01", "2024-01-31"]
            }
        ]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"PressOperations.productionDate": "2024-01-15", "PressOperations.count": "120"}
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert "data" in result
    assert "PressOperations.productionDate" in result["data"][0]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_metadata_retrieval():
    """Test retrieving Cube.js metadata."""
    client = CubeJSClient()

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "cubes": [
            {
                "name": "PressOperations",
                "title": "Press Operations",
                "measures": [
                    {"name": "count", "title": "Count"},
                    {"name": "passRate", "title": "Pass Rate"}
                ],
                "dimensions": [
                    {"name": "partFamily", "title": "Part Family"},
                    {"name": "shiftId", "title": "Shift ID"}
                ]
            },
            {
                "name": "PartFamilyPerformance",
                "title": "Part Family Performance",
                "measures": [
                    {"name": "totalPartsProduced", "title": "Total Parts Produced"}
                ],
                "dimensions": [
                    {"name": "partFamily", "title": "Part Family"}
                ]
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        metadata = await client.get_meta()

    assert "cubes" in metadata
    assert len(metadata["cubes"]) == 2
    assert metadata["cubes"][0]["name"] == "PressOperations"
    assert len(metadata["cubes"][0]["measures"]) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_query_error_handling():
    """Test proper error handling for invalid Cube.js queries."""
    import httpx
    client = CubeJSClient()

    query = CubeQuery(
        measures=["InvalidCube.invalidMeasure"],
        dimensions=[]
    )

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Cube not found: InvalidCube"
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cube_query_with_limit():
    """Test Cube.js query respects limit parameter."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=["PressOperations.count"],
        dimensions=["PressOperations.operatorId"],
        limit=5
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"PressOperations.operatorId": f"OP_{i}", "PressOperations.count": f"{100+i}"}
            for i in range(5)
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    assert len(result["data"]) == 5


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_measures_single_dimension():
    """Test querying multiple measures with single dimension."""
    client = CubeJSClient()

    query = CubeQuery(
        measures=[
            "PressOperations.avgOee",
            "PressOperations.avgAvailability",
            "PressOperations.avgPerformance",
            "PressOperations.avgQualityRate"
        ],
        dimensions=["PressOperations.partFamily"]
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "PressOperations.partFamily": "Door_Outer_Left",
                "PressOperations.avgOee": "0.825",
                "PressOperations.avgAvailability": "0.90",
                "PressOperations.avgPerformance": "0.95",
                "PressOperations.avgQualityRate": "0.965"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch('httpx.AsyncClient') as mock_httpx:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__aenter__.return_value = mock_client

        result = await client.execute_query(query)

    # Verify all measures are returned
    data_point = result["data"][0]
    assert "PressOperations.avgOee" in data_point
    assert "PressOperations.avgAvailability" in data_point
    assert "PressOperations.avgPerformance" in data_point
    assert "PressOperations.avgQualityRate" in data_point
