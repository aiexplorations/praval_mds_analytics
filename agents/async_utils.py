"""
Async utilities for running coroutines from synchronous Praval agent handlers.

Praval agent handlers are synchronous, but they often need to call async functions
(e.g., HTTP clients, LLM APIs). This module provides utilities to safely run
async code from sync contexts without blocking an existing event loop.
"""
import asyncio
import concurrent.futures
import logging
from typing import TypeVar, Coroutine, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine from a synchronous context.

    Handles both cases:
    - No event loop running: Creates a new loop with asyncio.run()
    - Event loop already running: Uses a thread pool to avoid blocking

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of the coroutine

    Example:
        result = run_async(some_async_function(arg1, arg2))
    """
    try:
        # Check if there's already a running event loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop - safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # There's a running loop - run in a separate thread to avoid blocking
        logger.debug("Running async coroutine in thread pool (event loop already running)")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result(timeout=60)  # 60 second timeout
