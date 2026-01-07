"""Data extraction from source databases.

Extractors for automotive press manufacturing data:
- PressLineAExtractor: Door panel production from 800T press (Line A)
- PressLineBExtractor: Bonnet panel production from 1200T press (Line B)
- DieManagementExtractor: Die master data and condition assessments
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .database import DatabaseConnection
from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DataExtractor:
    """Base extractor for source databases."""

    def __init__(self, db_config: DatabaseConfig, source_name: str):
        """Initialize extractor.

        Args:
            db_config: Database configuration
            source_name: Name of the source (press_line_a, press_line_b, die_management)
        """
        self.db = DatabaseConnection(db_config)
        self.source_name = source_name

    def extract_all(self, table_name: str) -> List[Dict[str, Any]]:
        """Extract all rows from a table.

        Args:
            table_name: Name of the table to extract from

        Returns:
            List of rows as dictionaries
        """
        query = f"SELECT * FROM {table_name} ORDER BY id"
        logger.info(f"Extracting all data from {self.source_name}.{table_name}")

        try:
            data = self.db.execute_query(query)
            logger.info(f"Extracted {len(data)} rows from {self.source_name}.{table_name}")
            return data
        except Exception as e:
            logger.error(f"Failed to extract from {self.source_name}.{table_name}: {e}")
            raise

    def extract_incremental(
        self,
        table_name: str,
        last_sync_time: Optional[datetime] = None,
        timestamp_column: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """Extract rows modified since last sync.

        Args:
            table_name: Name of the table
            last_sync_time: Last sync timestamp
            timestamp_column: Column to use for incremental sync

        Returns:
            List of new/modified rows
        """
        if last_sync_time:
            query = f"""
                SELECT * FROM {table_name}
                WHERE {timestamp_column} > %s
                ORDER BY id
            """
            logger.info(
                f"Extracting incremental data from {self.source_name}.{table_name} "
                f"since {last_sync_time}"
            )
            data = self.db.execute_query(query, (last_sync_time,))
        else:
            logger.info(f"No last sync time, extracting all data from {table_name}")
            data = self.extract_all(table_name)

        logger.info(f"Extracted {len(data)} rows from {self.source_name}.{table_name}")
        return data

    def get_max_timestamp(self, table_name: str, timestamp_column: str = "timestamp") -> Optional[datetime]:
        """Get the maximum timestamp from a table.

        Args:
            table_name: Name of the table
            timestamp_column: Timestamp column name

        Returns:
            Maximum timestamp or None if table is empty
        """
        query = f"SELECT MAX({timestamp_column}) as max_ts FROM {table_name}"
        result = self.db.execute_query(query)

        if result and result[0]['max_ts']:
            return result[0]['max_ts']
        return None

    def close(self):
        """Close database connection."""
        self.db.close()


class PressLineAExtractor(DataExtractor):
    """Extractor for Press Line A (800T) door panel production data."""

    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "press_line_a")
        self.table_name = "press_line_a_production"

    def extract(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract Press Line A production data.

        Args:
            incremental: Whether to do incremental extraction
            last_sync_time: Last sync timestamp for incremental

        Returns:
            List of door panel production records
        """
        if incremental:
            return self.extract_incremental(self.table_name, last_sync_time)
        return self.extract_all(self.table_name)


class PressLineBExtractor(DataExtractor):
    """Extractor for Press Line B (1200T) bonnet panel production data."""

    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "press_line_b")
        self.table_name = "press_line_b_production"

    def extract(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract Press Line B production data.

        Args:
            incremental: Whether to do incremental extraction
            last_sync_time: Last sync timestamp for incremental

        Returns:
            List of bonnet panel production records
        """
        if incremental:
            return self.extract_incremental(self.table_name, last_sync_time)
        return self.extract_all(self.table_name)


class DieManagementExtractor(DataExtractor):
    """Extractor for die management data (master, changeover, condition)."""

    def __init__(self, db_config: DatabaseConfig):
        super().__init__(db_config, "die_management")
        self.die_master_table = "die_master"
        self.changeover_table = "die_changeover_events"
        self.condition_table = "die_condition_assessments"

    def extract(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract die master data.

        Args:
            incremental: Whether to do incremental extraction
            last_sync_time: Last sync timestamp for incremental

        Returns:
            List of die master records
        """
        # Die master uses updated_at for incremental sync
        if incremental and last_sync_time:
            return self.extract_incremental(self.die_master_table, last_sync_time, "updated_at")
        return self.extract_all_dies()

    def extract_all_dies(self) -> List[Dict[str, Any]]:
        """Extract all die master records (ordered by die_id, not id)."""
        query = f"SELECT * FROM {self.die_master_table} ORDER BY die_id"
        logger.info(f"Extracting all data from {self.source_name}.{self.die_master_table}")

        try:
            data = self.db.execute_query(query)
            logger.info(f"Extracted {len(data)} rows from {self.source_name}.{self.die_master_table}")
            return data
        except Exception as e:
            logger.error(f"Failed to extract from {self.source_name}.{self.die_master_table}: {e}")
            raise

    def extract_changeover_events(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract die changeover events."""
        if incremental and last_sync_time:
            return self.extract_incremental(self.changeover_table, last_sync_time, "changeover_timestamp")
        return self.extract_all(self.changeover_table)

    def extract_condition_assessments(self, incremental: bool = False, last_sync_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Extract die condition assessments."""
        if incremental and last_sync_time:
            return self.extract_incremental(self.condition_table, last_sync_time, "assessment_timestamp")
        return self.extract_all(self.condition_table)


# Backward compatibility aliases (deprecated - use new names)
RefillsExtractor = PressLineAExtractor
BodiesExtractor = PressLineBExtractor
SpringsExtractor = DieManagementExtractor
