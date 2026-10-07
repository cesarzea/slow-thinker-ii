"""Reading runs: summaries with the live status of active runs, run views and event pages."""

from collections.abc import Mapping

from ._active import ActiveRun
from ._errors import RunNotFound
from ._ports import RunStore
from ._records import RecordedEvent, RunRecord
from ._views import EventPage, RunView, run_view

MAX_RUNS = 100
MAX_EVENTS = 500
TERMINAL = frozenset({"completed", "stopped", "failed", "cancelled"})


class RunQueries:
    def __init__(self, store: RunStore, active: Mapping[str, ActiveRun]) -> None:
        self._store = store
        self._active = active

    def record(self, run_id: str) -> RunRecord:
        record = self._store.run(run_id)
        if record is None:
            raise RunNotFound(run_id)
        return self._live(record)

    def view(self, run_id: str) -> RunView:
        return run_view(self.record(run_id), self.all_events(run_id))

    def runs(self, graph_id: str | None, limit: int) -> tuple[RunRecord, ...]:
        bounded = min(max(limit, 1), MAX_RUNS)
        return tuple(self._live(record) for record in self._store.runs(graph_id, bounded))

    def events(self, run_id: str, after: int, limit: int) -> EventPage:
        """A page of events; `finished` once the run is terminal and the page ends its log."""
        terminal = self.record(run_id).status in TERMINAL
        bounded = min(max(limit, 1), MAX_EVENTS)
        found = self._store.events(run_id, after, bounded + 1)
        page = found[:bounded]
        last_seq = page[-1].seq if page else after
        return EventPage(page, last_seq, terminal and len(found) <= bounded)

    def all_events(self, run_id: str) -> list[RecordedEvent]:
        events: list[RecordedEvent] = []
        while True:
            page = self._store.events(run_id, events[-1].seq if events else 0, MAX_EVENTS)
            events.extend(page)
            if len(page) < MAX_EVENTS:
                return events

    def _live(self, record: RunRecord) -> RunRecord:
        """The stored record, with `running` once an active run's trigger has fired."""
        active = self._active.get(record.run_id)
        if active is None or record.status != "starting":
            return record
        return RunRecord(
            record.run_id,
            record.graph_id,
            record.version,
            record.change,
            active.status(),
            record.reason,
            record.detail,
            record.input,
            record.created_at,
            record.ended_at,
            record.totals,
        )
