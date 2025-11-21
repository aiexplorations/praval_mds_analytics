"""Tests for database connection manager."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from database import Database


class TestDatabase:
    """Test suite for Database connection manager."""

    @pytest.fixture
    def db(self):
        """Create database instance."""
        return Database()

    @pytest.mark.asyncio
    async def test_connect_success(self, db):
        """Test successful database connection."""
        mock_pool = MagicMock()

        with patch("asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)):
            await db.connect()
            assert db.pool == mock_pool

    @pytest.mark.asyncio
    async def test_connect_with_settings(self, db):
        """Test connection uses settings correctly."""
        mock_pool = MagicMock()

        with patch("asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)) as mock_create:
            await db.connect()

            # Verify create_pool was called with correct parameters
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs

            assert call_kwargs["host"] == "postgres-warehouse"
            assert call_kwargs["port"] == 5432
            assert call_kwargs["database"] == "warehouse"
            assert call_kwargs["user"] == "warehouse_user"
            assert call_kwargs["min_size"] == 2
            assert call_kwargs["max_size"] == 10

    @pytest.mark.asyncio
    async def test_disconnect_success(self, db):
        """Test successful disconnection."""
        mock_pool = MagicMock()
        mock_pool.close = AsyncMock()
        db.pool = mock_pool

        await db.disconnect()

        mock_pool.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_pool(self, db):
        """Test disconnect when pool is None."""
        db.pool = None

        # Should not raise exception
        await db.disconnect()

    @pytest.mark.asyncio
    async def test_execute_success(self, db):
        """Test executing query successfully."""
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(return_value="OK")

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.execute("INSERT INTO test VALUES ($1)", "value")

        assert result == "OK"
        mock_conn.execute.assert_called_once_with("INSERT INTO test VALUES ($1)", "value")

    @pytest.mark.asyncio
    async def test_fetch_success(self, db):
        """Test fetching multiple rows."""
        mock_rows = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]

        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=mock_rows)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.fetch("SELECT * FROM test WHERE id > $1", 0)

        assert result == mock_rows
        assert len(result) == 2
        mock_conn.fetch.assert_called_once_with("SELECT * FROM test WHERE id > $1", 0)

    @pytest.mark.asyncio
    async def test_fetch_empty_result(self, db):
        """Test fetch with no results."""
        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=[])

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.fetch("SELECT * FROM test WHERE id = $1", 999)

        assert result == []

    @pytest.mark.asyncio
    async def test_fetchrow_success(self, db):
        """Test fetching single row."""
        mock_row = {"id": 1, "name": "test"}

        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value=mock_row)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.fetchrow("SELECT * FROM test WHERE id = $1", 1)

        assert result == mock_row
        mock_conn.fetchrow.assert_called_once_with("SELECT * FROM test WHERE id = $1", 1)

    @pytest.mark.asyncio
    async def test_fetchrow_not_found(self, db):
        """Test fetchrow when row doesn't exist."""
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.fetchrow("SELECT * FROM test WHERE id = $1", 999)

        assert result is None

    @pytest.mark.asyncio
    async def test_fetchval_success(self, db):
        """Test fetching single value."""
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=42)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.fetchval("SELECT COUNT(*) FROM test")

        assert result == 42
        mock_conn.fetchval.assert_called_once_with("SELECT COUNT(*) FROM test")

    @pytest.mark.asyncio
    async def test_fetchval_with_args(self, db):
        """Test fetchval with query arguments."""
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=True)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        result = await db.fetchval("SELECT EXISTS(SELECT 1 FROM test WHERE id = $1)", 1)

        assert result is True
        mock_conn.fetchval.assert_called_once_with(
            "SELECT EXISTS(SELECT 1 FROM test WHERE id = $1)", 1
        )

    @pytest.mark.asyncio
    async def test_multiple_operations(self, db):
        """Test performing multiple database operations."""
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(return_value="OK")
        mock_conn.fetch = AsyncMock(return_value=[{"id": 1}])
        mock_conn.fetchval = AsyncMock(return_value=1)

        mock_pool = MagicMock()
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

        db.pool = mock_pool

        # Execute insert
        await db.execute("INSERT INTO test VALUES ($1)", "value")

        # Fetch results
        rows = await db.fetch("SELECT * FROM test")
        assert len(rows) == 1

        # Get count
        count = await db.fetchval("SELECT COUNT(*) FROM test")
        assert count == 1


class TestDatabaseGlobalInstance:
    """Test the global database instance."""

    def test_db_instance_exists(self):
        """Test that global db instance is created."""
        from database import db

        assert db is not None
        assert isinstance(db, Database)

    def test_db_singleton_pattern(self):
        """Test that importing db returns same instance."""
        from database import db as db1
        from database import db as db2

        assert db1 is db2
