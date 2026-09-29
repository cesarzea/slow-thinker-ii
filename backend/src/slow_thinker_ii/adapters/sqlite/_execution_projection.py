"""Page combined activation and call entries without mixing live snapshot boundaries."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._execution_state import activation_view, communication_view
from ._operator_cursors import OperatorCursors


def execution_page(
    db: sqlite3.Connection,
    run: str,
    cursor: str | None,
    cursors: OperatorCursors,
    size: int,
    generation: str,
) -> JsonObject | None:
    record = db.execute(
        "SELECT graph_revision,event_sequence FROM managed_runs WHERE run_id=?", (run,)
    ).fetchone()
    if record is None:
        return None
    scope = "execution:" + generation + ":" + run
    upper, after = window(cursors, scope, int(record["event_sequence"]), cursor)
    through = upper // 2
    rows = execution_rows(db, run, through, after, size)
    activations, calls = execution_views(db, run, rows[:size], through)
    return {
        "run_id": run,
        "graph_revision": str(record["graph_revision"]),
        "backend_generation": generation,
        "through_sequence": through,
        "activations": activations,
        "calls": calls,
        "next_cursor": cursors.encode(scope, upper, int(rows[size - 1]["position"]))
        if len(rows) > size
        else None,
    }


def execution_rows(
    db: sqlite3.Connection, run: str, through: int, after: int, size: int
) -> list[sqlite3.Row]:
    return db.execute(
        "WITH entries AS ("
        "SELECT e.sequence*2 AS position,'call' AS kind,e.sequence,c.* FROM run_events e "
        "JOIN managed_calls c USING(call_id) WHERE e.run_id=? AND "
        "e.event='call.requested' AND e.sequence<=? "
        "UNION ALL SELECT e.sequence*2+1 AS position,'activation' AS kind,e.sequence,c.* "
        "FROM run_events e "
        "JOIN managed_calls c USING(call_id) WHERE e.run_id=? AND "
        "e.event='call.requested' AND e.sequence<=? "
        "AND c.parent_call_id IS NULL AND json_extract(c.context_json,'$.activation_id') "
        "IS NOT NULL) "
        "SELECT * FROM entries WHERE position>? ORDER BY position LIMIT ?",
        (run, through, run, through, after, size + 1),
    ).fetchall()


def execution_views(
    db: sqlite3.Connection, run: str, rows: list[sqlite3.Row], through: int
) -> tuple[list[JsonValue], list[JsonValue]]:
    activations: list[JsonValue] = []
    calls: list[JsonValue] = []
    for row in rows:
        if row["kind"] == "activation":
            activations.append(activation_view(db, run, row, through))
        else:
            calls.append(communication_view(db, run, row, through))
    return activations, calls


def window(
    cursors: OperatorCursors, scope: str, sequence: int, cursor: str | None
) -> tuple[int, int]:
    return (sequence * 2 + 1, 0) if cursor is None else cursors.decode(cursor, scope)
