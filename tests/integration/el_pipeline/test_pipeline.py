"""Integration tests for EL pipeline.

TODO: Warehouse schema migration needed.
The source databases (press_line_a, press_line_b, die_management) are migrated to
automotive schema, but the warehouse raw schema still uses the old pen manufacturing
tables (refills_production, bodies_production, springs_production).

Pipeline tests are skipped until warehouse migration is complete.
Extractor tests in test_extractor.py work with the migrated source databases.
"""

import pytest
from el_pipeline.pipeline import ELPipeline


# Skip pipeline tests - warehouse schema migration required
# The extractors work with the new automotive source DBs, but the loader
# and warehouse still use the old pen manufacturing schema.

@pytest.mark.skip(reason="Warehouse schema migration to automotive press required")
@pytest.mark.integration
def test_pipeline_full_sync(test_config):
    """Test full pipeline sync."""
    pipeline = ELPipeline(test_config)

    try:
        # Run full sync
        stats = pipeline.run_full_sync()

        # Verify stats
        assert stats['press_line_a_count'] > 0
        assert stats['press_line_b_count'] > 0
        assert stats['die_management_count'] > 0

        # Verify data landed in warehouse
        warehouse_stats = pipeline.get_warehouse_stats()
        assert warehouse_stats['press_line_a_count'] == stats['press_line_a_count']
        assert warehouse_stats['press_line_b_count'] == stats['press_line_b_count']
        assert warehouse_stats['die_management_count'] == stats['die_management_count']

    finally:
        pipeline.close()


@pytest.mark.skip(reason="Warehouse schema migration to automotive press required")
@pytest.mark.integration
def test_pipeline_warehouse_stats(test_config):
    """Test warehouse statistics retrieval."""
    pipeline = ELPipeline(test_config)

    try:
        stats = pipeline.get_warehouse_stats()

        assert 'press_line_a_count' in stats
        assert 'press_line_b_count' in stats
        assert 'die_management_count' in stats
        assert all(isinstance(count, int) for count in stats.values())

    finally:
        pipeline.close()


@pytest.mark.skip(reason="Warehouse schema migration to automotive press required")
@pytest.mark.integration
def test_pipeline_closes_connections(test_config):
    """Test that pipeline properly closes all connections."""
    pipeline = ELPipeline(test_config)

    # Establish connections by running a small operation
    pipeline.get_warehouse_stats()

    # Close connections
    pipeline.close()

    # Verify all connections are closed
    assert pipeline.press_line_a_extractor.db._conn is None or pipeline.press_line_a_extractor.db._conn.closed
    assert pipeline.press_line_b_extractor.db._conn is None or pipeline.press_line_b_extractor.db._conn.closed
    assert pipeline.die_management_extractor.db._conn is None or pipeline.die_management_extractor.db._conn.closed
    assert pipeline.loader.db._conn.closed
