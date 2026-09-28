"""Backend-owned read projections include shared balances and backend continuity."""

import time
from collections.abc import Callable
from uuid import uuid4

from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ._database import SqliteDatabase
from ._operator_cleanup import blocker
from ._operator_cursors import OperatorCursors
from ._operator_pages import RUN_SELECT, OperatorPages
from ._operator_profiles import current_profile, period
from ._operator_projection import budget, run_details
from ._operator_result import final_result
from ._trace_activations import activation_details
from ._trace_calls import call_details
from ._trace_events import event_page
from ._trace_payloads import payload_details


class SqliteOperatorQueries:
    def __init__(
        self,
        database: SqliteDatabase,
        cursor_key: bytes,
        page_size: int = 50,
        wall: Callable[[], float] = time.time,
    ) -> None:
        if type(page_size) is not int or not 1 <= page_size <= 100:
            raise ValueError("An operator page contains between 1 and 100 records")
        self._database, self._wall = database, wall
        self._cursors, self._size = OperatorCursors(cursor_key), page_size
        self._pages = OperatorPages(self._cursors, page_size)
        self._generation = uuid4().hex

    def workspace(self, cursor: str | None = None) -> str:
        with self._database.transaction() as db:
            month = period(self._wall())
            profile = current_profile(db)
            blocked = blocker(db, cache=False)
            reason = (
                "no_configuration" if profile is None else (None if blocked is None else blocked[0])
            )
            return encode_json(
                {
                    "schema_version": "0.1-draft",
                    "backend_generation": self._generation,
                    "sessions": self._pages.sessions(db, cursor),
                    "configuration_revision": None if profile is None else profile.revision,
                    "limits": None if profile is None else decode_json(profile.limits.to_json()),
                    "admission_available": reason is None,
                    "admission_reason": reason,
                    "blocking_run_id": None if blocked is None else blocked[1],
                    "month_budget": budget(
                        db, "month", month, 0 if profile is None else profile.limits.month_budget
                    ),
                }
            )

    def run(self, run_id: str) -> str | None:
        with self._database.transaction() as db:
            row = db.execute(RUN_SELECT + "WHERE r.run_id=?", (run_id,)).fetchone()
            if row is None:
                return None
            value = run_details(db, row, period(self._wall()))
            value["schema_version"], value["backend_generation"] = "0.1-draft", self._generation
            return encode_json(value)

    def definition(self, run_id: str) -> str | None:
        with self._database.transaction() as db:
            row = db.execute(RUN_SELECT + "WHERE r.run_id=?", (run_id,)).fetchone()
            if row is None:
                return None
            snapshot = json_object(decode_json(str(row["snapshot_json"])))
            return encode_json(
                {
                    "schema_version": "0.1-draft",
                    "run_id": run_id,
                    "execution": snapshot.get("execution", {}),
                }
            )

    def session_runs(self, session_id: str, cursor: str | None = None) -> str | None:
        with self._database.transaction() as db:
            if (
                db.execute(
                    "SELECT 1 FROM operator_sessions WHERE session_id=?", (session_id,)
                ).fetchone()
                is None
            ):
                return None
            value = self._pages.runs(db, session_id, cursor)
            value["session_id"], value["backend_generation"] = session_id, self._generation
            value["schema_version"] = "0.1-draft"
            value["budget"] = budget(db, "session", session_id)
            return encode_json(value)

    def result(self, run_id: str) -> str | None:
        with self._database.transaction() as db:
            return final_result(db, run_id)

    def events(self, run_id: str, cursor: str | None = None) -> str | None:
        with self._database.transaction() as db:
            value = event_page(db, run_id, cursor, self._cursors, self._size)
            return None if value is None else encode_json(value)

    def call(self, run_id: str, call_id: str, cursor: str | None = None) -> str | None:
        with self._database.transaction() as db:
            value = call_details(db, run_id, call_id, cursor, self._cursors, self._size)
            return None if value is None else encode_json(value)

    def payload(self, run_id: str, payload_id: str) -> str | None:
        with self._database.transaction() as db:
            value = payload_details(db, run_id, payload_id)
            return None if value is None else encode_json(value)

    def activation(self, run_id: str, activation_id: str, cursor: str | None = None) -> str | None:
        with self._database.transaction() as db:
            value = activation_details(db, run_id, activation_id, cursor, self._cursors, self._size)
            return None if value is None else encode_json(value)
