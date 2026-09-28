"""Bound list reads to a stable row window without SQL supplied by the caller."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._operator_cursors import OperatorCursors
from ._operator_projection import run_summary

RUN_SELECT = (
    "SELECT r.*,o.created_at,o.rowid AS position FROM operator_runs o "
    "JOIN managed_runs r USING(run_id) "
)


class OperatorPages:
    def __init__(self, cursors: OperatorCursors, size: int) -> None:
        self._cursors, self._size = cursors, size

    def sessions(self, db: sqlite3.Connection, cursor: str | None) -> JsonObject:
        upper = int(
            db.execute("SELECT COALESCE(MAX(rowid),0) FROM operator_sessions").fetchone()[0]
        )
        through, after = (upper, 0) if cursor is None else self._cursors.decode(cursor, "sessions")
        rows = db.execute(
            "SELECT rowid AS position,* FROM operator_sessions WHERE rowid>? AND rowid<=? "
            "ORDER BY rowid LIMIT ?",
            (after, through, self._size + 1),
        ).fetchall()
        items: list[JsonValue] = [
            {
                "session_id": str(row["session_id"]),
                "name": str(row["name"]),
                "created_at": float(row["created_at"]),
            }
            for row in rows[: self._size]
        ]
        return self._page("sessions", through, rows, items)

    def runs(self, db: sqlite3.Connection, session: str, cursor: str | None) -> JsonObject:
        scope = "runs:" + session
        upper = int(
            db.execute(
                "SELECT COALESCE(MAX(o.rowid),0) FROM operator_runs o "
                "JOIN managed_runs r USING(run_id) WHERE r.session_id=?",
                (session,),
            ).fetchone()[0]
        )
        through, after = (upper, 0) if cursor is None else self._cursors.decode(cursor, scope)
        rows = db.execute(
            RUN_SELECT + "WHERE r.session_id=? AND o.rowid>? AND o.rowid<=? "
            "ORDER BY o.rowid LIMIT ?",
            (session, after, through, self._size + 1),
        ).fetchall()
        items: list[JsonValue] = [run_summary(db, row) for row in rows[: self._size]]
        return self._page(scope, through, rows, items)

    def _page(
        self, scope: str, through: int, rows: list[sqlite3.Row], items: list[JsonValue]
    ) -> JsonObject:
        more = len(rows) > self._size
        cursor = (
            self._cursors.encode(scope, through, int(rows[self._size - 1]["position"]))
            if more
            else None
        )
        return {"items": items, "next_cursor": cursor}
