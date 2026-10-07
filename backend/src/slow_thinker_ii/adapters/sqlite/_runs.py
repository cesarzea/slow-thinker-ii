"""`RunStore`: run summaries and their append-only event logs."""

import sqlite3
from datetime import datetime

from slow_thinker_ii.application import NewEvent, RecordedEvent, RunNotFound, RunRecord
from slow_thinker_ii.contracts import JsonObject, json_object

from ._database import SqliteDatabase
from ._payloads import bounded
from ._rows import dump, integer, stamp, text
from ._run_rows import recorded_event, run_record

INSERT_RUN = (
    "INSERT INTO runs (id, graph_id, graph_version, graph_change, status, reason, detail, "
    "input_json, created_at, ended_at, totals_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
INSERT_EVENT = (
    "INSERT INTO run_events (run_id, seq, at, elapsed_ms, kind, evidence, node_id, "
    "activation_id, data_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


class SqliteRunStore:
    """Payload-like fields above `max_payload_bytes` are truncated before they are stored."""

    def __init__(self, database: SqliteDatabase, max_payload_bytes: int = 262_144) -> None:
        self._database = database
        self._max_payload_bytes = max_payload_bytes

    def create(self, run: RunRecord) -> None:
        ended = None if run.ended_at is None else stamp(run.ended_at)
        totals = None if run.totals is None else dump(run.totals)
        source = (run.run_id, run.graph_id, run.version, run.change)
        values = (*source, run.status, run.reason, run.detail)
        with self._database.transaction() as connection:
            connection.execute(
                INSERT_RUN, (*values, dump(run.input), stamp(run.created_at), ended, totals)
            )

    def append(self, run_id: str, event: NewEvent) -> RecordedEvent:
        """Appends the event with the run's next `seq` in its own transaction."""
        data = json_object(bounded(event.data, self._max_payload_bytes))
        at, kind, evidence = stamp(event.at), event.kind, event.evidence
        with self._database.transaction() as connection:
            seq = integer(
                connection.execute(
                    "SELECT coalesce(max(seq), 0) + 1 AS seq FROM run_events WHERE run_id = ?",
                    (run_id,),
                ).fetchone(),
                "seq",
            )
            ids = (event.node_id, event.activation_id)
            row = (run_id, seq, at, event.elapsed_ms, kind, evidence, *ids, dump(data))
            connection.execute(INSERT_EVENT, row)
        return RecordedEvent(run_id, seq, event.at, event.elapsed_ms, kind, evidence, *ids, data)

    def finish(
        self,
        run_id: str,
        status: str,
        reason: str | None,
        detail: str,
        totals: JsonObject,
        at: datetime,
    ) -> None:
        """Records the terminal status once; an unknown run raises `RunNotFound`."""
        with self._database.transaction() as connection:
            changed = connection.execute(
                "UPDATE runs SET status = ?, reason = ?, detail = ?, totals_json = ?, ended_at = ? "
                "WHERE id = ? AND ended_at IS NULL",
                (status, reason, detail, dump(totals), stamp(at), run_id),
            ).rowcount
            if changed == 0 and _exists(connection, run_id):
                raise ValueError(f"Run “{run_id}” is already finished.")
        if changed == 0:
            raise RunNotFound(run_id)

    def run(self, run_id: str) -> RunRecord | None:
        with self._database.transaction() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return None if row is None else run_record(row)

    def runs(self, graph_id: str | None, limit: int) -> tuple[RunRecord, ...]:
        """Runs of one graph, or of all graphs, the newest first."""
        with self._database.transaction() as connection:
            rows = connection.execute(
                "SELECT * FROM runs WHERE ? IS NULL OR graph_id = ? "
                "ORDER BY created_at DESC, rowid DESC LIMIT ?",
                (graph_id, graph_id, max(limit, 0)),
            ).fetchall()
        return tuple(run_record(row) for row in rows)

    def events(self, run_id: str, after: int, limit: int) -> tuple[RecordedEvent, ...]:
        """Events with `seq` greater than `after`, in order, at most `limit`."""
        with self._database.transaction() as connection:
            rows = connection.execute(
                "SELECT * FROM run_events WHERE run_id = ? AND seq > ? ORDER BY seq LIMIT ?",
                (run_id, after, max(limit, 0)),
            ).fetchall()
        return tuple(recorded_event(row) for row in rows)

    def unfinished(self) -> tuple[str, ...]:
        """Runs without a terminal status, the oldest first."""
        with self._database.transaction() as connection:
            rows = connection.execute(
                "SELECT id FROM runs WHERE ended_at IS NULL ORDER BY created_at, rowid"
            ).fetchall()
        return tuple(text(row, "id") for row in rows)


def _exists(connection: sqlite3.Connection, run_id: str) -> bool:
    return connection.execute("SELECT 1 FROM runs WHERE id = ?", (run_id,)).fetchone() is not None
