"""Ports the adapters implement: stores, the budget ledger, host launching, providers, clock."""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from slow_thinker_ii import engine
from slow_thinker_ii.accounting import Scope
from slow_thinker_ii.contracts import JsonObject
from slow_thinker_ii.graphs import RunPlan

from ._graph_port import GraphStore as GraphStore
from ._records import NewEvent, RecordedEvent, RunRecord
from ._values import LlmModel, ProviderReply


class RunStore(Protocol):
    def create(self, run: RunRecord) -> None: ...

    def append(self, run_id: str, event: NewEvent) -> RecordedEvent:
        """Appends an event with the run's next `seq`, assigned atomically."""
        ...

    def finish(
        self,
        run_id: str,
        status: str,
        reason: str | None,
        detail: str,
        totals: JsonObject,
        at: datetime,
    ) -> None: ...

    def run(self, run_id: str) -> RunRecord | None: ...

    def runs(self, graph_id: str | None, limit: int) -> tuple[RunRecord, ...]:
        """Runs of one graph, or of all graphs, the newest first."""
        ...

    def events(self, run_id: str, after: int, limit: int) -> tuple[RecordedEvent, ...]:
        """Events with `seq` greater than `after`, in order, at most `limit`."""
        ...

    def unfinished(self) -> tuple[str, ...]:
        """Identifiers of runs that have no terminal status."""
        ...


class Ledger(Protocol):
    def reserve(
        self, call_id: str, run_id: str, scopes: Sequence[Scope], amount: int, at: datetime
    ) -> Scope | None:
        """Reserves `amount` in every scope atomically, or returns the first exhausted scope.

        Callers pass `used=0`; the ledger reads each scope's used amount (settled charges plus
        open reservations) in the same transaction and returns the exhausted scope with it.
        """
        ...

    def settle(self, call_id: str, charge: int, estimated: bool, at: datetime) -> None: ...

    def used(self, kind: str, key: str) -> int: ...

    def settle_open(self, run_id: str, at: datetime) -> None:
        """Restart recovery: open reservations of the run become estimated charges."""
        ...


class RunHosts(engine.Hosts, Protocol):
    async def close(self) -> None:
        """Stops every host of the run; never raises."""
        ...


class HostLauncher(Protocol):
    async def launch(self, run_id: str, plan: RunPlan, log: engine.RunLog) -> RunHosts:
        """Launches and checks every package host, recording `host.ready` or `host.failed`.

        Raises `StartupFailed` with an English detail when any host fails.
        """
        ...


class LlmProvider(Protocol):
    async def complete(
        self, model: LlmModel, request: JsonObject, timeout_s: float
    ) -> ProviderReply:
        """One provider attempt. `timeout_s` is the call's remaining time; the adapter applies
        the smaller of it and the provider's configured timeout and returns 504 when exceeded."""
        ...


class Clock(engine.Clock, Protocol):
    def now(self) -> datetime:
        """Aware UTC time."""
        ...
