"""Own and cancel the backend's independent tariff refresh tasks."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import ExitStack, asynccontextmanager, suppress
from time import time

from fastapi import FastAPI

from slow_thinker_ii.adapters.process import recover_processes
from slow_thinker_ii.adapters.sqlite import (
    SqliteConfigurationCommands,
    SqliteDatabase,
    SqliteProcessJournal,
    SqliteRunStore,
)
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
        additional: tuple[TariffRefresh, ...] = (),
    ) -> None:
        self._database, self._refresh, self._execution = database, refresh, execution
        self._additional = additional
        self._lease = ExitStack()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None]:
        del app
        self._lease.enter_context(self._database.ownership())
        tasks: list[asyncio.Task[None]] = []
        try:
            tasks = await self._start()
            yield
        finally:
            await self._stop(tasks)

    async def _start(self) -> list[asyncio.Task[None]]:
        self._database.initialize()
        recover_runs(SqliteRunStore(self._database, 1_048_576))
        await recover_processes(SqliteProcessJournal(self._database, 1_048_576), 5)
        if self._execution is not None:
            SqliteConfigurationCommands(self._database).initialize(self._execution.configuration)
        refreshes = (self._refresh, *self._additional)
        await asyncio.gather(
            *(refresh.refresh_due(int(time()), startup=True) for refresh in refreshes)
        )
        return [
            asyncio.create_task(refresh_loop(refresh), name=f"tariff-refresh-{index}")
            for index, refresh in enumerate(refreshes)
        ]

    async def _stop(self, tasks: list[asyncio.Task[None]]) -> None:
        for task in tasks:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        if self._execution is not None and not await self._execution.close():
            raise RuntimeError("Incomplete execution shutdown; database ownership retained")
        self._lease.close()
