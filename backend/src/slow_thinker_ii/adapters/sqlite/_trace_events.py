"""Event pages expose durable order and references within a fixed run boundary."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._operator_cursors import OperatorCursors


def event_page(
    db: sqlite3.Connection, run: str, cursor: str | None, cursors: OperatorCursors, size: int
) -> JsonObject | None:
    row = db.execute("SELECT event_sequence FROM managed_runs WHERE run_id=?", (run,)).fetchone()
    if row is None:
        return None
    scope = "events:" + run
    through, after = (int(row[0]), 0) if cursor is None else cursors.decode(cursor, scope)
    rows = db.execute(
        "SELECT sequence,event,call_id,received_at FROM run_events "
        "WHERE run_id=? AND sequence>? AND sequence<=? ORDER BY sequence LIMIT ?",
        (run, after, through, size + 1),
    ).fetchall()
    items: list[JsonValue] = [event_item(item) for item in rows[:size]]
    next_cursor = (
        cursors.encode(scope, through, int(rows[size - 1]["sequence"]))
        if len(rows) > size
        else None
    )
    return {
        "schema_version": "0.1-draft",
        "run_id": run,
        "through_sequence": through,
        "items": items,
        "next_cursor": next_cursor,
    }


def event_item(row: sqlite3.Row) -> JsonObject:
    sequence = int(row["sequence"])
    return {
        "sequence": sequence,
        "event": str(row["event"]),
        "call_id": row["call_id"],
        "received_at": str(row["received_at"]),
        "payload_id": f"event:{sequence}",
    }
