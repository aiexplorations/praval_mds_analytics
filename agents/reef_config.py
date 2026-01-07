"""
Reef Configuration for Praval Multi-Agent System.

Initializes the Reef (message queue network) and channels for agent communication.
"""
import logging
from praval import get_reef
from praval.core.reef import Reef

logger = logging.getLogger(__name__)

# Global Reef instance
_reef_instance: Reef = None


def initialize_reef() -> Reef:
    """
    Initialize the Reef with default configuration.

    Creates the main communication channel for agent-to-agent Spore exchange.

    Returns:
        Reef instance
    """
    global _reef_instance

    if _reef_instance is not None:
        logger.info("Reef already initialized, returning existing instance")
        return _reef_instance

    logger.info("Initializing Praval Reef...")

    # Get the global Reef instance from Praval
    _reef_instance = get_reef()

    # Create specialized channels (optional - main channel exists by default)
    # All agents will use the default "main" channel for simplicity
    # Future: could create separate channels like "analytics", "quality", "visualization"

    logger.info("Reef initialized successfully")
    logger.info(f"Reef instance: {_reef_instance}")

    return _reef_instance


def get_reef_instance() -> Reef:
    """
    Get the current Reef instance.

    Returns:
        Reef instance

    Raises:
        RuntimeError: If Reef not initialized
    """
    if _reef_instance is None:
        raise RuntimeError("Reef not initialized. Call initialize_reef() first.")

    return _reef_instance


def cleanup_reef():
    """
    Cleanup Reef resources (if needed for graceful shutdown).

    Currently a no-op as Praval's in-memory Reef doesn't require cleanup,
    but included for future extensibility (e.g., if using RabbitMQ backend).
    """
    global _reef_instance

    if _reef_instance is not None:
        logger.info("Cleaning up Reef...")
        # Future: Add cleanup logic if using persistent backend
        _reef_instance = None
        logger.info("Reef cleaned up")
