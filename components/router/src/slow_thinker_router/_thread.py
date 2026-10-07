"""Run the synchronous script in a daemon thread so that the host stays responsive."""

import asyncio
import threading
from contextlib import suppress
from dataclasses import dataclass

from slow_thinker_host import JsonValue

from ._script import Route


@dataclass(frozen=True)
class Outcome:
    """What one script call returned, or the exception it raised."""

    value: object = None
    error: BaseException | None = None


async def call_route(route: Route, received: JsonValue, node_input: JsonValue) -> Outcome:
    """Await one call; a script that never returns is abandoned, never awaited at exit."""
    loop = asyncio.get_running_loop()
    future: asyncio.Future[Outcome] = loop.create_future()

    def run() -> None:
        try:
            outcome = Outcome(value=route(received, node_input))
        except (Exception, SystemExit) as error:
            outcome = Outcome(error=error)
        with suppress(RuntimeError):  # The loop closed while the script ran.
            loop.call_soon_threadsafe(_settle, future, outcome)

    threading.Thread(target=run, name="router-script", daemon=True).start()
    return await future


def _settle(future: asyncio.Future[Outcome], outcome: Outcome) -> None:
    if not future.done():
        future.set_result(outcome)
