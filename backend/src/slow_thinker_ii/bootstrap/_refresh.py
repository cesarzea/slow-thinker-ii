"""Own and cancel the backend's single tariff refresh task."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import ExitStack, asynccontextmanager, suppress
from time import time

from fastapi import FastAPI

from slow_thinker_ii.adapters.process import recover_processes
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteProcessJournal, SqliteRunStore
from slow_thinker_ii.application import REFRESH_SECONDS, TariffRefresh, recover_runs

from ._execution import ExecutionServices


async def refresh_loop(refresh: TariffRefresh) -> None:
    while True:
        status = await refresh.refresh_due(int(time()))
        elapsed = time() - (status.last_attempt or 0)
        await asyncio.sleep(max(1, REFRESH_SECONDS - elapsed))


class TariffLifetime:
    def __init__(
        self,
        database: SqliteDatabase,
        refresh: TariffRefresh,
        execution: ExecutionServices | None = None,
    ) -> None:
        self._database, self._refresh, self._execution = database, refresh, execution
        self._lease = ExitStack()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None]:
        del app
        self._lease.enter_context(self._database.ownership())
        task: asyncio.Task[None] | None = None
        try:
            self._database.initialize()
            recover_runs(SqliteRunStore(self._database, 1_048_576))
            await recover_processes(SqliteProcessJournal(self._database, 1_048_576), 5)
            if self._execution is not None:
                self._execution.commands.configure(self._execution.configuration)
            await self._refresh.refresh_due(int(time()), startup=True)
            task = asyncio.create_task(refresh_loop(self._refresh), name="tariff-refresh")
            yield
        finally:
            if task is not None:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
            if self._execution is not None and not await self._execution.close():
                raise RuntimeError("Incomplete execution shutdown; database ownership retained")
            self._lease.close()
