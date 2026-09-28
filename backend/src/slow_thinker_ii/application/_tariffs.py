"""Daily refresh orchestration; failed imports never replace validated prices."""

import asyncio
from typing import Protocol

from slow_thinker_ii.accounting import RefreshStatus, TariffRevision

REFRESH_SECONDS = 24 * 60 * 60


class TariffSource(Protocol):
    async def fetch(self, now: int) -> TariffRevision: ...


class TariffStore(Protocol):
    def status(self) -> RefreshStatus: ...
    def publish(self, revision: TariffRevision) -> None: ...
    def failed(self, now: int, error: str) -> None: ...
    def revision(self, digest: str) -> TariffRevision: ...


class TariffRefresh:
    def __init__(self, source: TariffSource, store: TariffStore) -> None:
        self._source = source
        self._store = store
        self._lock = asyncio.Lock()

    async def refresh_due(self, now: int, *, startup: bool = False) -> RefreshStatus:
        async with self._lock:
            status = self._store.status()
            if status.last_attempt is not None and now < status.last_attempt:
                return status
            previous = status.last_success if startup else status.last_attempt
            if previous is not None and now - previous < REFRESH_SECONDS:
                return status
            try:
                revision = await self._source.fetch(now)
            except (OSError, ValueError, TimeoutError) as error:
                self._store.failed(now, type(error).__name__)
            else:
                self._store.publish(revision)
            return self._store.status()
