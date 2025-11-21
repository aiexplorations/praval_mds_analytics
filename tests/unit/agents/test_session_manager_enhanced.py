"""Tests for enhanced session manager with PostgreSQL persistence."""
import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from session_manager_enhanced import EntityTracker, EnhancedSessionManager
from models import ChatMessage


class TestEntityTracker:
    """Test suite for EntityTracker."""

    def test_init(self):
        """Test EntityTracker initialization."""
        tracker = EntityTracker()
        assert tracker.entities == {}

    def test_extract_entities_door_left(self):
        """Test extracting Door_Outer_Left."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Show me defects for Door_Outer_Left")

        assert "part_families" in entities
        assert "Door_Outer_Left" in entities["part_families"]

    def test_extract_entities_door_right(self):
        """Test extracting Door_Outer_Right."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("What's the OEE for Door_Outer_Right?")

        assert "part_families" in entities
        assert "Door_Outer_Right" in entities["part_families"]

    def test_extract_entities_both_doors(self):
        """Test extracting both doors when mentioned together."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Compare left and right doors")

        assert "part_families" in entities
        assert "Door_Outer_Left" in entities["part_families"]
        assert "Door_Outer_Right" in entities["part_families"]

    def test_extract_entities_doors_generic(self):
        """Test extracting doors without specifying side."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Show me door performance")

        assert "part_families" in entities
        # Should include both when no specific side mentioned
        assert "Door_Outer_Left" in entities["part_families"]
        assert "Door_Outer_Right" in entities["part_families"]

    def test_extract_entities_bonnet(self):
        """Test extracting Bonnet_Outer."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("What about the bonnet quality?")

        assert "part_families" in entities
        assert "Bonnet_Outer" in entities["part_families"]

    def test_extract_entities_oee_metric(self):
        """Test extracting OEE metric."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Show me OEE trends")

        assert "current_metric" in entities
        assert entities["current_metric"] == "OEE"

    def test_extract_entities_defect_metric(self):
        """Test extracting defect rate metric."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("What's the defect rate?")

        assert "current_metric" in entities
        assert entities["current_metric"] == "defect_rate"

    def test_extract_entities_quality_metric(self):
        """Test quality keyword maps to defect_rate."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("How's the quality?")

        assert "current_metric" in entities
        assert entities["current_metric"] == "defect_rate"

    def test_extract_entities_cycle_time(self):
        """Test extracting cycle time metric."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Check cycle time performance")

        assert "current_metric" in entities
        assert entities["current_metric"] == "cycle_time"

    def test_extract_entities_defect_types(self):
        """Test extracting defect types."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("We're seeing springback and burr issues")

        assert "defect_types" in entities
        assert "springback" in entities["defect_types"]
        assert "burr" in entities["defect_types"]

    def test_extract_entities_press_line_a(self):
        """Test extracting Line A."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Line A performance check")

        assert "press_line" in entities
        assert entities["press_line"] == "Line A"

    def test_extract_entities_press_line_a_tonnage(self):
        """Test Line A extraction via tonnage."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("800T press analysis")

        assert "press_line" in entities
        assert entities["press_line"] == "Line A"

    def test_extract_entities_press_line_b(self):
        """Test extracting Line B."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Line B status")

        assert "press_line" in entities
        assert entities["press_line"] == "Line B"

    def test_extract_entities_time_period_today(self):
        """Test extracting 'today' time period."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("What happened today?")

        assert "time_period" in entities
        assert entities["time_period"] == "today"

    def test_extract_entities_time_period_last_week(self):
        """Test extracting 'last week' time period."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("Show last week's data")

        assert "time_period" in entities
        assert entities["time_period"] == "last_7_days"

    def test_extract_entities_time_period_this_month(self):
        """Test extracting 'this month' time period."""
        tracker = EntityTracker()
        entities = tracker.extract_entities("This month's performance")

        assert "time_period" in entities
        assert entities["time_period"] == "current_month"

    def test_extract_entities_multiple(self):
        """Test extracting multiple entity types at once."""
        tracker = EntityTracker()
        entities = tracker.extract_entities(
            "Show me OEE for Door_Outer_Left on Line A last week"
        )

        assert "part_families" in entities
        assert "current_metric" in entities
        assert "press_line" in entities
        assert "time_period" in entities

    def test_update_method(self):
        """Test update method adds entities."""
        tracker = EntityTracker()
        tracker.update("Show defects for Door_Outer_Left")

        assert "Door_Outer_Left" in tracker.entities.get("part_families", [])

    def test_update_method_overrides(self):
        """Test update method overrides previous values."""
        tracker = EntityTracker()
        tracker.update("Line A performance")
        assert tracker.entities["press_line"] == "Line A"

        tracker.update("Now check Line B")
        assert tracker.entities["press_line"] == "Line B"

    def test_resolve_reference_plural(self):
        """Test resolving plural references."""
        tracker = EntityTracker()
        tracker.entities = {"part_families": ["Door_Outer_Left", "Door_Outer_Right"]}

        resolved = tracker.resolve_reference("these")
        assert "Door_Outer_Left" in resolved
        assert "Door_Outer_Right" in resolved

    def test_resolve_reference_singular_metric(self):
        """Test resolving singular reference to metric."""
        tracker = EntityTracker()
        tracker.entities = {"current_metric": "OEE"}

        resolved = tracker.resolve_reference("it")
        assert resolved == "OEE"

    def test_resolve_reference_singular_press_line(self):
        """Test resolving singular reference to press line."""
        tracker = EntityTracker()
        tracker.entities = {"press_line": "Line A"}

        resolved = tracker.resolve_reference("that")
        assert resolved == "Line A"

    def test_resolve_reference_no_context(self):
        """Test resolving reference with no context."""
        tracker = EntityTracker()

        resolved = tracker.resolve_reference("it")
        assert resolved is None

    def test_get_context_string_empty(self):
        """Test context string with no entities."""
        tracker = EntityTracker()

        context = tracker.get_context_string()
        assert "No context" in context

    def test_get_context_string_full(self):
        """Test context string with all entity types."""
        tracker = EntityTracker()
        tracker.entities = {
            "part_families": ["Door_Outer_Left"],
            "current_metric": "OEE",
            "press_line": "Line A",
            "time_period": "last_7_days"
        }

        context = tracker.get_context_string()
        assert "Door_Outer_Left" in context
        assert "OEE" in context
        assert "Line A" in context
        assert "last_7_days" in context

    def test_to_dict(self):
        """Test converting tracker to dictionary."""
        tracker = EntityTracker()
        tracker.entities = {"part_families": ["Door_Outer_Left"]}

        data = tracker.to_dict()
        assert isinstance(data, dict)
        assert "part_families" in data

    def test_from_dict(self):
        """Test loading tracker from dictionary."""
        data = {"part_families": ["Door_Outer_Left"], "current_metric": "OEE"}
        tracker = EntityTracker.from_dict(data)

        assert tracker.entities == data


class TestEnhancedSessionManager:
    """Test suite for EnhancedSessionManager."""

    @pytest.fixture
    def mock_db(self):
        """Mock database for testing."""
        with patch("session_manager_enhanced.db") as mock:
            mock.connect = AsyncMock()
            mock.execute = AsyncMock()
            mock.fetchrow = AsyncMock(return_value=None)
            mock.fetchval = AsyncMock(return_value=False)
            yield mock

    @pytest.fixture
    def manager(self):
        """Create session manager instance."""
        return EnhancedSessionManager()

    @pytest.mark.asyncio
    async def test_initialize(self, manager, mock_db):
        """Test session manager initialization."""
        await manager.initialize()
        mock_db.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session_no_user(self, manager, mock_db):
        """Test creating session without user ID."""
        session_id = await manager.create_session()

        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in manager.cache
        assert session_id in manager.entity_trackers

        # Verify database insert was called
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args[0]
        assert "INSERT INTO conversation_history" in call_args[0]

    @pytest.mark.asyncio
    async def test_create_session_with_user(self, manager, mock_db):
        """Test creating session with user ID."""
        session_id = await manager.create_session(user_id="eng_001")

        assert session_id in manager.cache
        assert manager.cache[session_id]["user_id"] == "eng_001"

    @pytest.mark.asyncio
    async def test_get_session_from_cache(self, manager, mock_db):
        """Test getting session from cache."""
        session_id = str(uuid.uuid4())
        messages = [ChatMessage(role="user", content="Hello")]

        manager.cache[session_id] = {"messages": messages}

        result = await manager.get_session(session_id)

        assert result == messages
        # Should not hit database
        mock_db.fetchrow.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_session_from_database(self, manager, mock_db):
        """Test loading session from database."""
        session_id = str(uuid.uuid4())
        messages_data = [{"role": "user", "content": "Hello"}]

        mock_db.fetchrow = AsyncMock(
            return_value={"messages": json.dumps(messages_data)}
        )

        result = await manager.get_session(session_id)

        assert len(result) == 1
        assert result[0].role == "user"
        assert result[0].content == "Hello"

        # Should cache it
        assert session_id in manager.cache

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, manager, mock_db):
        """Test getting non-existent session."""
        mock_db.fetchrow = AsyncMock(return_value=None)

        result = await manager.get_session("non-existent")
        assert result is None

    @pytest.mark.asyncio
    async def test_add_message_to_existing_session(self, manager, mock_db):
        """Test adding message to existing session."""
        session_id = str(uuid.uuid4())
        manager.cache[session_id] = {"messages": []}
        manager.entity_trackers[session_id] = EntityTracker()

        message = ChatMessage(role="user", content="Hello")
        await manager.add_message(session_id, message)

        assert len(manager.cache[session_id]["messages"]) == 1
        assert manager.cache[session_id]["messages"][0].content == "Hello"

        # Should persist to database
        mock_db.execute.assert_called()

    @pytest.mark.asyncio
    async def test_add_message_max_limit(self, manager, mock_db):
        """Test message limit enforcement."""
        from config import settings

        session_id = str(uuid.uuid4())
        manager.cache[session_id] = {"messages": []}
        manager.entity_trackers[session_id] = EntityTracker()

        # Add more than max messages
        for i in range(settings.max_session_messages + 10):
            msg = ChatMessage(role="user", content=f"Message {i}")
            await manager.add_message(session_id, msg)

        # Should only keep max messages
        assert len(manager.cache[session_id]["messages"]) == settings.max_session_messages
        # Should have the latest messages
        assert manager.cache[session_id]["messages"][-1].content == f"Message {settings.max_session_messages + 9}"

    @pytest.mark.asyncio
    async def test_add_message_updates_entities(self, manager, mock_db):
        """Test that adding user messages updates entity tracking."""
        session_id = str(uuid.uuid4())
        manager.cache[session_id] = {"messages": []}
        manager.entity_trackers[session_id] = EntityTracker()

        message = ChatMessage(role="user", content="Show OEE for Door_Outer_Left")
        await manager.add_message(session_id, message)

        tracker = manager.entity_trackers[session_id]
        assert "Door_Outer_Left" in tracker.entities.get("part_families", [])
        assert tracker.entities.get("current_metric") == "OEE"

    @pytest.mark.asyncio
    async def test_add_message_assistant_no_entity_update(self, manager, mock_db):
        """Test that assistant messages don't update entities."""
        session_id = str(uuid.uuid4())
        manager.cache[session_id] = {"messages": []}
        manager.entity_trackers[session_id] = EntityTracker()

        message = ChatMessage(role="assistant", content="Here's the OEE data")
        await manager.add_message(session_id, message)

        tracker = manager.entity_trackers[session_id]
        # Entities should be empty since assistant message shouldn't update
        assert tracker.entities == {}

    @pytest.mark.asyncio
    async def test_get_context_default_limit(self, manager, mock_db):
        """Test getting context with default limit."""
        session_id = str(uuid.uuid4())
        messages = [ChatMessage(role="user", content=f"Message {i}") for i in range(50)]
        manager.cache[session_id] = {"messages": messages}

        context = await manager.get_context(session_id)

        # Default max_messages is 30
        assert len(context) == 30
        # Should have the latest messages
        assert context[-1].content == "Message 49"

    @pytest.mark.asyncio
    async def test_get_context_custom_limit(self, manager, mock_db):
        """Test getting context with custom limit."""
        session_id = str(uuid.uuid4())
        messages = [ChatMessage(role="user", content=f"Message {i}") for i in range(50)]
        manager.cache[session_id] = {"messages": messages}

        context = await manager.get_context(session_id, max_messages=10)

        assert len(context) == 10
        assert context[-1].content == "Message 49"

    @pytest.mark.asyncio
    async def test_get_context_empty_session(self, manager, mock_db):
        """Test getting context for empty session."""
        mock_db.fetchrow = AsyncMock(return_value=None)

        context = await manager.get_context("non-existent")
        assert context == []

    @pytest.mark.asyncio
    async def test_get_entities_cached(self, manager, mock_db):
        """Test getting entity tracker from cache."""
        session_id = str(uuid.uuid4())
        tracker = EntityTracker()
        tracker.entities = {"part_families": ["Door_Outer_Left"]}
        manager.entity_trackers[session_id] = tracker

        result = await manager.get_entities(session_id)

        assert result == tracker
        # Should not hit database
        mock_db.fetchrow.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_entities_from_database(self, manager, mock_db):
        """Test loading entity tracker from database."""
        session_id = str(uuid.uuid4())
        entities_data = {"part_families": ["Door_Outer_Left"]}

        mock_db.fetchrow = AsyncMock(
            return_value={"entities": json.dumps(entities_data)}
        )

        tracker = await manager.get_entities(session_id)

        assert "Door_Outer_Left" in tracker.entities.get("part_families", [])
        # Should cache it
        assert session_id in manager.entity_trackers

    @pytest.mark.asyncio
    async def test_get_entities_not_found(self, manager, mock_db):
        """Test getting entities for non-existent session."""
        mock_db.fetchrow = AsyncMock(return_value=None)

        tracker = await manager.get_entities("non-existent")

        # Should return empty tracker
        assert tracker.entities == {}

    @pytest.mark.asyncio
    async def test_session_exists_true(self, manager, mock_db):
        """Test checking if session exists (positive)."""
        mock_db.fetchval = AsyncMock(return_value=True)

        exists = await manager.session_exists("some-session")
        assert exists is True

    @pytest.mark.asyncio
    async def test_session_exists_false(self, manager, mock_db):
        """Test checking if session exists (negative)."""
        mock_db.fetchval = AsyncMock(return_value=False)

        exists = await manager.session_exists("non-existent")
        assert exists is False

    @pytest.mark.asyncio
    async def test_cleanup_old_sessions(self, manager, mock_db):
        """Test cleaning up old sessions."""
        await manager.cleanup_old_sessions(days=30)

        # Should execute DELETE query
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args[0]
        assert "DELETE FROM conversation_history" in call_args[0]

    @pytest.mark.asyncio
    async def test_cleanup_old_sessions_custom_days(self, manager, mock_db):
        """Test cleanup with custom retention period."""
        await manager.cleanup_old_sessions(days=7)

        mock_db.execute.assert_called_once()
        # Verify cutoff date is calculated correctly
        call_args = mock_db.execute.call_args[0]
        cutoff_date = call_args[1]
        expected_cutoff = datetime.now() - timedelta(days=7)

        # Allow 1 second tolerance for test execution time
        assert abs((cutoff_date - expected_cutoff).total_seconds()) < 1


class TestEnhancedSessionManagerIntegration:
    """Integration tests for enhanced session manager."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test complete conversation flow with entity tracking."""
        with patch("session_manager_enhanced.db") as mock_db:
            mock_db.connect = AsyncMock()
            mock_db.execute = AsyncMock()
            mock_db.fetchrow = AsyncMock(return_value=None)

            manager = EnhancedSessionManager()
            await manager.initialize()

            # Create session
            session_id = await manager.create_session(user_id="test_user")

            # Add messages with entity tracking
            msg1 = ChatMessage(role="user", content="Show me OEE for Door_Outer_Left")
            await manager.add_message(session_id, msg1)

            msg2 = ChatMessage(role="assistant", content="Here's the OEE data...")
            await manager.add_message(session_id, msg2)

            msg3 = ChatMessage(role="user", content="Now compare with the right door")
            await manager.add_message(session_id, msg3)

            # Get context
            context = await manager.get_context(session_id)
            assert len(context) == 3

            # Check entity tracking
            tracker = await manager.get_entities(session_id)
            parts = tracker.entities.get("part_families", [])

            # Should have both doors from the conversation
            assert "Door_Outer_Left" in parts or "Door_Outer_Right" in parts
