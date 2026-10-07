"""The server's lifetime: own and prepare the database, recover, serve, then stop active runs."""

from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

from fastapi import FastAPI

from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from slow_thinker_ii.application import RunService

type Lifespan = Callable[[FastAPI], AbstractAsyncContextManager[None]]


class SystemClock:
    """The one clock of the services and of their grants: aware UTC time and monotonic seconds."""

    def now(self) -> datetime:
        return datetime.now(UTC)

    def monotonic(self) -> float:
        return monotonic()


def lifespan(database: SqliteDatabase, runs: RunService, workspace: Path) -> Lifespan:
    """Startup takes the owner lock, initializes the schema and recovers unfinished runs."""

    @asynccontextmanager
    async def serve(_app: FastAPI) -> AsyncGenerator[None]:
        with database.ownership():
            database.initialize()
            workspace.mkdir(parents=True, exist_ok=True)
            runs.recover()
            try:
                yield
            finally:
                await runs.shutdown()

    return serve
