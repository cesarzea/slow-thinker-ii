"""Waiting for background work without sleeping: the event loop runs until a condition holds."""

import asyncio
from collections.abc import Callable


async def until(condition: Callable[[], bool], attempts: int = 500) -> None:
    """Lets other tasks run until `condition` holds; fails after `attempts` loop iterations."""
    for _ in range(attempts):
        if condition():
            return
        await asyncio.sleep(0)
    raise AssertionError("The awaited condition did not hold")
