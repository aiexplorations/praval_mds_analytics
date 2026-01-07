"""Pytest configuration and fixtures."""

import pytest
from el_pipeline.config import PipelineConfig, DatabaseConfig


@pytest.fixture
def test_config():
    """Provide test configuration for automotive press analytics."""
    return PipelineConfig(
        refills_db=DatabaseConfig(
            host="localhost",
            port=5436,
            database="press_line_a",
            user="press_a_user",
            password="press_a_pass",
        ),
        bodies_db=DatabaseConfig(
            host="localhost",
            port=5437,
            database="press_line_b",
            user="press_b_user",
            password="press_b_pass",
        ),
        springs_db=DatabaseConfig(
            host="localhost",
            port=5438,
            database="die_management",
            user="die_mgmt_user",
            password="die_mgmt_pass",
        ),
        warehouse_db=DatabaseConfig(
            host="localhost",
            port=5435,
            database="warehouse",
            user="warehouse_user",
            password="warehouse_pass",
        ),
        batch_size=100,
        log_level="DEBUG",
    )


@pytest.fixture
def db_config():
    """Provide database configuration for testing."""
    return DatabaseConfig(
        host="localhost",
        port=5436,
        database="press_line_a",
        user="press_a_user",
        password="press_a_pass",
    )
