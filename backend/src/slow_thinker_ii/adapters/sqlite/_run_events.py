"""Append run-ordered evidence in the same transaction as its state change."""

import sqlite3

from slow_thinker_ii.application import RunEvent

from ._rows import integer, text
from ._run_rows import bounded_json


def append_event(
    connection: sqlite3.Connection,
    run_id: str,
    event: str,
    call_id: str | None,
    payload: str,
    limit: int,
) -> None:
    bounded_json(connection, payload, limit)
    changed = connection.execute(
        "UPDATE managed_runs SET event_sequence=event_sequence+1 "
        "WHERE run_id=? RETURNING event_sequence",
        (run_id,),
    ).fetchone()
    if changed is None:
        raise ValueError("Unknown event run")
    connection.execute(
        "INSERT INTO run_events(run_id,sequence,event,call_id,payload_json) VALUES(?,?,?,?,?)",
        (run_id, changed[0], event, call_id, payload),
    )


def read_events(connection: sqlite3.Connection, run_id: str) -> tuple[RunEvent, ...]:
    rows = connection.execute(
        "SELECT * FROM run_events WHERE run_id=? ORDER BY sequence", (run_id,)
    )
    return tuple(
        RunEvent(
            integer(row, "sequence"),
            text(row, "event"),
            None if row["call_id"] is None else text(row, "call_id"),
            text(row, "payload_json"),
        )
        for row in rows
    )
