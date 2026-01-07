"""Tests for data extractor - Automotive Press Manufacturing.

Tests for EL pipeline extractors:
- PressLineAExtractor: Door panel production from 800T press
- PressLineBExtractor: Bonnet panel production from 1200T press
- DieManagementExtractor: Die master and condition data
"""

import pytest
from el_pipeline.extractor import PressLineAExtractor, PressLineBExtractor, DieManagementExtractor
from el_pipeline.config import DatabaseConfig


@pytest.mark.integration
def test_press_line_a_extractor(test_config):
    """Test Press Line A (door panel) data extraction."""
    extractor = PressLineAExtractor(test_config.refills_db)  # refills_db maps to press_line_a

    try:
        data = extractor.extract(incremental=False)

        assert len(data) > 0
        assert 'id' in data[0]
        assert 'part_id' in data[0]
        assert 'press_line_id' in data[0]
        assert 'part_family' in data[0]
        assert 'quality_status' in data[0]
        assert 'oee' in data[0]
    finally:
        extractor.close()


@pytest.mark.integration
def test_press_line_b_extractor(test_config):
    """Test Press Line B (bonnet panel) data extraction."""
    extractor = PressLineBExtractor(test_config.bodies_db)  # bodies_db maps to press_line_b

    try:
        data = extractor.extract(incremental=False)

        assert len(data) > 0
        assert 'id' in data[0]
        assert 'part_id' in data[0]
        assert 'press_line_id' in data[0]
        assert 'part_family' in data[0]
        assert 'quality_status' in data[0]
        assert 'oee' in data[0]
    finally:
        extractor.close()


@pytest.mark.integration
def test_die_management_extractor(test_config):
    """Test die management data extraction."""
    extractor = DieManagementExtractor(test_config.springs_db)  # springs_db maps to die_management

    try:
        data = extractor.extract(incremental=False)

        assert len(data) > 0
        assert 'die_id' in data[0]
        assert 'part_family' in data[0]
        assert 'die_type' in data[0]
        assert 'health_status' in data[0]
    finally:
        extractor.close()


@pytest.mark.integration
def test_extractor_get_max_timestamp(test_config):
    """Test getting maximum timestamp from table."""
    extractor = PressLineAExtractor(test_config.refills_db)

    try:
        max_ts = extractor.get_max_timestamp("press_line_a_production")
        assert max_ts is not None
    finally:
        extractor.close()


@pytest.mark.integration
def test_incremental_extraction(test_config):
    """Test incremental data extraction."""
    extractor = PressLineAExtractor(test_config.refills_db)

    try:
        # Get max timestamp
        max_ts = extractor.get_max_timestamp("press_line_a_production")

        # Extract incremental data (should be empty since we're using max timestamp)
        data = extractor.extract(incremental=True, last_sync_time=max_ts)

        # Should return empty or very few records
        assert isinstance(data, list)
    finally:
        extractor.close()
