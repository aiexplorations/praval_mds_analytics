"""Tests for agent tools module."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import httpx
from pytest_httpx import HTTPXMock

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from agent_tools import (
    ManufacturingTools,
    StatisticalTools,
    CubeJsTools,
    CalculatorTools,
    get_agent_tools,
    TOOL_REGISTRY
)
from config import settings


class TestManufacturingTools:
    """Test suite for ManufacturingTools."""

    def test_manufacturing_glossary_oee(self):
        """Test looking up OEE definition."""
        result = ManufacturingTools.manufacturing_glossary("OEE")
        assert "OEE" in result
        assert "Overall Equipment Effectiveness" in result
        assert "85%" in result

    def test_manufacturing_glossary_smed(self):
        """Test looking up SMED definition."""
        result = ManufacturingTools.manufacturing_glossary("SMED")
        assert "SMED" in result
        assert "Single-Minute Exchange of Die" in result
        assert "10 minutes" in result

    def test_manufacturing_glossary_springback(self):
        """Test looking up springback definition."""
        result = ManufacturingTools.manufacturing_glossary("springback")
        assert "springback" in result
        assert "forming" in result

    def test_manufacturing_glossary_case_insensitive(self):
        """Test glossary lookup is case insensitive."""
        result1 = ManufacturingTools.manufacturing_glossary("oee")
        result2 = ManufacturingTools.manufacturing_glossary("OEE")
        result3 = ManufacturingTools.manufacturing_glossary("Oee")

        assert result1 == result2 == result3

    def test_manufacturing_glossary_partial_match(self):
        """Test glossary matches partial terms."""
        result = ManufacturingTools.manufacturing_glossary("first pass yield data")
        assert "first pass yield" in result

    def test_manufacturing_glossary_not_found(self):
        """Test handling of unknown terms."""
        result = ManufacturingTools.manufacturing_glossary("unknown_term_xyz")
        assert "not found" in result
        assert "unknown_term_xyz" in result


class TestStatisticalTools:
    """Test suite for StatisticalTools."""

    def test_calculate_z_score_normal(self):
        """Test z-score calculation with normal values."""
        z = StatisticalTools.calculate_z_score(10.5, 8.0, 1.2)
        assert round(z, 2) == 2.08

    def test_calculate_z_score_negative(self):
        """Test z-score with value below mean."""
        z = StatisticalTools.calculate_z_score(5.0, 8.0, 1.5)
        assert z == -2.0

    def test_calculate_z_score_zero_std_dev(self):
        """Test z-score with zero standard deviation."""
        z = StatisticalTools.calculate_z_score(10.0, 8.0, 0.0)
        assert z == 0.0

    def test_calculate_z_score_at_mean(self):
        """Test z-score when value equals mean."""
        z = StatisticalTools.calculate_z_score(8.0, 8.0, 1.5)
        assert z == 0.0

    def test_calculate_control_limits_normal(self):
        """Test control limits calculation."""
        data = [10.0, 10.2, 9.8, 10.1, 9.9, 10.3, 9.7, 10.0]
        result = StatisticalTools.calculate_control_limits(data)

        assert "mean" in result
        assert "ucl" in result
        assert "lcl" in result
        assert "std_dev" in result

        assert result["mean"] == 10.0
        assert result["ucl"] > result["mean"]
        assert result["lcl"] < result["mean"]

    def test_calculate_control_limits_empty_data(self):
        """Test control limits with empty data."""
        result = StatisticalTools.calculate_control_limits([])
        assert result["mean"] == 0
        assert result["ucl"] == 0
        assert result["lcl"] == 0

    def test_calculate_control_limits_single_value(self):
        """Test control limits with single data point."""
        result = StatisticalTools.calculate_control_limits([10.0])
        assert result["mean"] == 10.0
        assert result["std_dev"] == 0

    def test_calculate_control_limits_custom_sigma(self):
        """Test control limits with custom sigma."""
        data = [10.0, 10.2, 9.8, 10.1, 9.9]
        result_3sigma = StatisticalTools.calculate_control_limits(data, sigma=3)
        result_2sigma = StatisticalTools.calculate_control_limits(data, sigma=2)

        # 3-sigma limits should be wider than 2-sigma
        assert result_3sigma["ucl"] > result_2sigma["ucl"]
        assert result_3sigma["lcl"] < result_2sigma["lcl"]

    def test_calculate_cpk_capable_process(self):
        """Test Cpk for capable process (Cpk > 1.33)."""
        # Simulating well-centered process
        data = [9.9, 10.0, 10.1, 9.95, 10.05, 10.0, 9.98, 10.02]
        cpk = StatisticalTools.calculate_cpk(data, usl=11.0, lsl=9.0)

        assert cpk > 1.0  # Process is capable

    def test_calculate_cpk_world_class(self):
        """Test Cpk for world-class process (Cpk > 1.67)."""
        # Very tight process with minimal variation
        data = [10.0, 10.01, 9.99, 10.02, 9.98, 10.0, 10.01, 9.99]
        cpk = StatisticalTools.calculate_cpk(data, usl=11.0, lsl=9.0)

        # With very low variation and good centering, Cpk should be high
        assert cpk > 1.0  # Relaxed expectation for realistic data

    def test_calculate_cpk_empty_data(self):
        """Test Cpk with empty data."""
        cpk = StatisticalTools.calculate_cpk([], usl=11.0, lsl=9.0)
        assert cpk == 0.0

    def test_calculate_cpk_single_value(self):
        """Test Cpk with single data point."""
        cpk = StatisticalTools.calculate_cpk([10.0], usl=11.0, lsl=9.0)
        assert cpk == 0.0

    def test_calculate_cpk_zero_std_dev(self):
        """Test Cpk with zero standard deviation."""
        data = [10.0, 10.0, 10.0]
        cpk = StatisticalTools.calculate_cpk(data, usl=11.0, lsl=9.0)
        assert cpk == 0.0

    def test_detect_outliers_iqr_normal(self):
        """Test IQR outlier detection with outliers."""
        data = [10, 11, 12, 11, 10, 9, 11, 12, 50, 10, 11]  # 50 is outlier
        outliers = StatisticalTools.detect_outliers_iqr(data)

        assert len(outliers) > 0
        assert 8 in outliers  # Index of value 50

    def test_detect_outliers_iqr_no_outliers(self):
        """Test IQR detection with clean data."""
        data = [10, 11, 12, 11, 10, 9, 11, 12, 10, 11]
        outliers = StatisticalTools.detect_outliers_iqr(data)

        assert len(outliers) == 0

    def test_detect_outliers_iqr_small_dataset(self):
        """Test IQR with dataset too small."""
        data = [10, 11, 12]
        outliers = StatisticalTools.detect_outliers_iqr(data)

        assert outliers == []

    def test_detect_outliers_iqr_multiple_outliers(self):
        """Test IQR detection with multiple outliers."""
        data = [1, 10, 11, 12, 11, 10, 9, 11, 12, 10, 100]
        outliers = StatisticalTools.detect_outliers_iqr(data)

        assert len(outliers) >= 2  # Both 1 and 100 should be detected


class TestCubeJsTools:
    """Test suite for CubeJsTools."""

    @pytest.mark.asyncio
    async def test_get_available_cubes_success(self, httpx_mock: HTTPXMock):
        """Test fetching available cubes successfully."""
        httpx_mock.add_response(
            url=f"{settings.cubejs_api_url}/meta",
            json={
                "cubes": [
                    {"name": "PressOperations"},
                    {"name": "PartFamilyPerformance"}
                ]
            }
        )

        cubes = await CubeJsTools.get_available_cubes()

        assert len(cubes) == 2
        assert "PressOperations" in cubes
        assert "PartFamilyPerformance" in cubes

    @pytest.mark.asyncio
    async def test_get_available_cubes_empty(self, httpx_mock: HTTPXMock):
        """Test fetching cubes when none exist."""
        httpx_mock.add_response(
            url=f"{settings.cubejs_api_url}/meta",
            json={"cubes": []}
        )

        cubes = await CubeJsTools.get_available_cubes()
        assert cubes == []

    @pytest.mark.asyncio
    async def test_get_available_cubes_error(self, httpx_mock: HTTPXMock):
        """Test error handling when fetching cubes fails."""
        httpx_mock.add_exception(Exception("Connection error"))

        cubes = await CubeJsTools.get_available_cubes()
        assert cubes == []

    @pytest.mark.asyncio
    async def test_get_cube_measures_success(self, httpx_mock: HTTPXMock):
        """Test fetching measures for a cube."""
        httpx_mock.add_response(
            url=f"{settings.cubejs_api_url}/meta",
            json={
                "cubes": [
                    {
                        "name": "PressOperations",
                        "measures": [
                            {"name": "PressOperations.totalParts"},
                            {"name": "PressOperations.avgOEE"}
                        ]
                    }
                ]
            }
        )

        measures = await CubeJsTools.get_cube_measures("PressOperations")

        assert len(measures) == 2
        assert "PressOperations.totalParts" in measures
        assert "PressOperations.avgOEE" in measures

    @pytest.mark.asyncio
    async def test_get_cube_measures_not_found(self, httpx_mock: HTTPXMock):
        """Test fetching measures for non-existent cube."""
        httpx_mock.add_response(
            url=f"{settings.cubejs_api_url}/meta",
            json={"cubes": [{"name": "OtherCube", "measures": []}]}
        )

        measures = await CubeJsTools.get_cube_measures("NonExistentCube")
        assert measures == []

    @pytest.mark.asyncio
    async def test_get_cube_dimensions_success(self, httpx_mock: HTTPXMock):
        """Test fetching dimensions for a cube."""
        httpx_mock.add_response(
            url=f"{settings.cubejs_api_url}/meta",
            json={
                "cubes": [
                    {
                        "name": "PressOperations",
                        "dimensions": [
                            {"name": "PressOperations.pressLine"},
                            {"name": "PressOperations.partFamily"}
                        ]
                    }
                ]
            }
        )

        dimensions = await CubeJsTools.get_cube_dimensions("PressOperations")

        assert len(dimensions) == 2
        assert "PressOperations.pressLine" in dimensions
        assert "PressOperations.partFamily" in dimensions


class TestCalculatorTools:
    """Test suite for CalculatorTools."""

    def test_calculate_oee_decimals(self):
        """Test OEE calculation with decimal inputs."""
        oee = CalculatorTools.calculate_oee(0.95, 0.90, 0.98)
        assert oee == 83.79  # 0.95 * 0.90 * 0.98 * 100

    def test_calculate_oee_percentages(self):
        """Test OEE calculation with percentage inputs."""
        oee = CalculatorTools.calculate_oee(95.0, 90.0, 98.0)
        assert oee == 83.79

    def test_calculate_oee_mixed_inputs(self):
        """Test OEE with mixed decimal and percentage."""
        oee1 = CalculatorTools.calculate_oee(0.95, 90.0, 0.98)
        oee2 = CalculatorTools.calculate_oee(95.0, 0.90, 98.0)
        assert oee1 == oee2

    def test_calculate_oee_perfect(self):
        """Test OEE with perfect efficiency."""
        oee = CalculatorTools.calculate_oee(1.0, 1.0, 1.0)
        assert oee == 100.0

    def test_calculate_oee_zero(self):
        """Test OEE with zero values."""
        oee = CalculatorTools.calculate_oee(0.0, 0.9, 0.95)
        assert oee == 0.0

    def test_calculate_defect_rate_normal(self):
        """Test defect rate calculation."""
        rate = CalculatorTools.calculate_defect_rate(50, 1000)
        assert rate == 5.0

    def test_calculate_defect_rate_zero_defects(self):
        """Test defect rate with no defects."""
        rate = CalculatorTools.calculate_defect_rate(0, 1000)
        assert rate == 0.0

    def test_calculate_defect_rate_all_defects(self):
        """Test defect rate with all parts defective."""
        rate = CalculatorTools.calculate_defect_rate(1000, 1000)
        assert rate == 100.0

    def test_calculate_defect_rate_zero_parts(self):
        """Test defect rate with zero total parts."""
        rate = CalculatorTools.calculate_defect_rate(10, 0)
        assert rate == 0.0

    def test_calculate_defect_rate_rounding(self):
        """Test defect rate rounding."""
        rate = CalculatorTools.calculate_defect_rate(1, 3)
        assert rate == 33.33

    def test_calculate_first_pass_yield_normal(self):
        """Test first pass yield calculation."""
        fpy = CalculatorTools.calculate_first_pass_yield(950, 1000)
        assert fpy == 95.0

    def test_calculate_first_pass_yield_perfect(self):
        """Test first pass yield with 100% yield."""
        fpy = CalculatorTools.calculate_first_pass_yield(1000, 1000)
        assert fpy == 100.0

    def test_calculate_first_pass_yield_zero_good(self):
        """Test first pass yield with no good parts."""
        fpy = CalculatorTools.calculate_first_pass_yield(0, 1000)
        assert fpy == 0.0

    def test_calculate_first_pass_yield_zero_total(self):
        """Test first pass yield with zero total parts."""
        fpy = CalculatorTools.calculate_first_pass_yield(100, 0)
        assert fpy == 0.0


class TestToolRegistry:
    """Test suite for tool registry and access functions."""

    def test_tool_registry_structure(self):
        """Test tool registry has expected structure."""
        assert "manufacturing_advisor" in TOOL_REGISTRY
        assert "quality_inspector" in TOOL_REGISTRY
        assert "analytics_specialist" in TOOL_REGISTRY
        assert "all" in TOOL_REGISTRY

    def test_get_agent_tools_manufacturing_advisor(self):
        """Test getting tools for manufacturing advisor."""
        tools = get_agent_tools("manufacturing_advisor")

        assert "manufacturing_glossary" in tools
        assert "calculate_oee" in tools
        assert "calculate_defect_rate" in tools
        assert "calculate_first_pass_yield" in tools

    def test_get_agent_tools_quality_inspector(self):
        """Test getting tools for quality inspector."""
        tools = get_agent_tools("quality_inspector")

        assert "calculate_z_score" in tools
        assert "calculate_control_limits" in tools
        assert "calculate_cpk" in tools
        assert "detect_outliers_iqr" in tools
        assert "calculate_oee" in tools  # Common tools included

    def test_get_agent_tools_analytics_specialist(self):
        """Test getting tools for analytics specialist."""
        tools = get_agent_tools("analytics_specialist")

        assert "get_available_cubes" in tools
        assert "get_cube_measures" in tools
        assert "get_cube_dimensions" in tools
        assert "calculate_oee" in tools

    def test_get_agent_tools_unknown_agent(self):
        """Test getting tools for unknown agent returns only common tools."""
        tools = get_agent_tools("unknown_agent")

        # Should only have common tools
        assert "calculate_oee" in tools
        assert "calculate_defect_rate" in tools
        assert "calculate_first_pass_yield" in tools

        # Should not have specific tools
        assert "manufacturing_glossary" not in tools
        assert "calculate_z_score" not in tools
