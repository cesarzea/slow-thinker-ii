"""An in-memory `application.RunStore` that signals when each run is finished."""

import asyncio
from datetime import datetime

from slow_thinker_ii.application import NewEvent, RecordedEvent, RunRecord
from slow_thinker_ii.contracts import JsonObject, json_object

TERMINAL = frozenset({"completed", "stopped", "failed", "cancelled"})


class MemoryRunStore:
    """`RunStore` fake: gap-free `seq` per run and JSON-checked copies of event data.

    `await finished(run_id)` waits for `finish`; `appends_fail` makes `append` raise `OSError`
    to simulate an unavailable database.
    """

    def __init__(self) -> None:
        self.appends_fail = False
        self._runs: dict[str, RunRecord] = {}
        self._events: dict[str, list[RecordedEvent]] = {}
        self._finished: dict[str, asyncio.Event] = {}

    def create(self, run: RunRecord) -> None:
        self._runs[run.run_id] = run
        self._events[run.run_id] = []

    def append(self, run_id: str, event: NewEvent) -> RecordedEvent:
        if self.appends_fail:
            raise OSError("The run store is unavailable.")
        events = self._events[run_id]
        recorded = RecordedEvent(
            run_id,
            len(events) + 1,
            event.at,
            event.elapsed_ms,
            event.kind,
            event.evidence,
            event.node_id,
            event.activation_id,
            json_object(event.data),
        )
        events.append(recorded)
        return recorded

    def finish(
        self,
        run_id: str,
        status: str,
        reason: str | None,
        detail: str,
        totals: JsonObject,
        at: datetime,
    ) -> None:
        run = self._runs[run_id]
        self._runs[run_id] = RunRecord(
            run.run_id,
            run.graph_id,
            run.version,
            run.change,
            status,
            reason,
            detail,
            run.input,
            run.created_at,
            at,
            json_object(totals),
        )
        self._signal(run_id).set()

    def run(self, run_id: str) -> RunRecord | None:
        return self._runs.get(run_id)

    def runs(self, graph_id: str | None, limit: int) -> tuple[RunRecord, ...]:
        newest = reversed(list(self._runs.values()))
        found = [run for run in newest if graph_id in (None, run.graph_id)]
        return tuple(found[:limit])

    def events(self, run_id: str, after: int, limit: int) -> tuple[RecordedEvent, ...]:
        later = [event for event in self._events.get(run_id, []) if event.seq > after]
        return tuple(later[:limit])

    def unfinished(self) -> tuple[str, ...]:
        return tuple(run.run_id for run in self._runs.values() if run.status not in TERMINAL)

    async def finished(self, run_id: str) -> RunRecord:
        await self._signal(run_id).wait()
        return self._runs[run_id]

    def kinds(self, run_id: str) -> list[str]:
        return [event.kind for event in self._events[run_id]]

    def of(self, run_id: str, kind: str) -> list[RecordedEvent]:
        return [event for event in self._events[run_id] if event.kind == kind]

    def _signal(self, run_id: str) -> asyncio.Event:
        return self._finished.setdefault(run_id, asyncio.Event())
