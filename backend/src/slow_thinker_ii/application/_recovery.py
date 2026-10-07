"""Restart recovery: runs left unfinished become `failed`, `interrupted`; reservations settle."""

import math

from slow_thinker_ii.contracts import JsonObject

from ._journal import Totals
from ._ports import Clock, Ledger, RunStore
from ._records import NewEvent
from ._run_queries import RunQueries

INTERRUPTED = "The backend restarted before the run finished."


class Recovery:
    def __init__(self, store: RunStore, ledger: Ledger, clock: Clock, queries: RunQueries) -> None:
        self._store = store
        self._ledger = ledger
        self._clock = clock
        self._queries = queries

    def recover(self) -> None:
        for run_id in self._store.unfinished():
            self._interrupt(run_id)

    def _interrupt(self, run_id: str) -> None:
        totals = Totals()
        for event in self._queries.all_events(run_id):
            totals.observe(event.kind, event.data)
        now = self._clock.now()
        record = self._store.run(run_id)
        admitted = now if record is None else record.created_at
        elapsed = max(0, math.floor((now - admitted).total_seconds() * 1000))
        document = totals.document(elapsed, totals.activations, totals.messages)
        data: JsonObject = {
            "status": "failed",
            "reason": "interrupted",
            "detail": INTERRUPTED,
            "totals": document,
            "dropped": totals.dropped,
        }
        self._store.append(
            run_id, NewEvent(now, elapsed, "run.finished", "observed", None, None, data)
        )
        self._store.finish(run_id, "failed", "interrupted", INTERRUPTED, document, now)
        self._ledger.settle_open(run_id, now)
