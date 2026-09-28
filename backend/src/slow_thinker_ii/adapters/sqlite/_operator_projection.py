"""Small projections are assembled within the caller's consistent read transaction."""

import sqlite3

from slow_thinker_ii.accounting import display_amount
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object

from ._operator_cleanup import confirmed


def budget(db: sqlite3.Connection, kind: str, identity: str, default: int = 0) -> JsonObject:
    row = db.execute(
        "SELECT cap,settled,reserved FROM budget_scopes WHERE kind=? AND scope_id=?",
        (kind, identity),
    ).fetchone()
    cap, spent, reserved = (default, 0, 0) if row is None else tuple(int(item) for item in row)
    return {
        "kind": kind,
        "scope_id": identity,
        "currency": "USD",
        "cap": display_amount(cap),
        "settled": display_amount(spent),
        "outstanding": display_amount(reserved),
        "available": display_amount(max(0, cap - spent - reserved)),
    }


def run_summary(db: sqlite3.Connection, row: sqlite3.Row) -> JsonObject:
    snapshot = json_object(decode_json(str(row["snapshot_json"])))
    intent = json_object(snapshot.get("intent", {}))
    identity = str(row["run_id"])
    cleanup = db.execute(
        "SELECT payload_json FROM run_events WHERE run_id=? AND event='run.cleanup' "
        "ORDER BY sequence DESC LIMIT 1",
        (identity,),
    ).fetchone()
    return {
        "run_id": identity,
        "session_id": str(row["session_id"]),
        "graph_id": intent.get("graph_id"),
        "graph_revision": str(row["graph_revision"]),
        "state": str(row["state"]),
        "reason": row["reason"],
        "created_at": float(row["created_at"]),
        "last_event_sequence": int(row["event_sequence"]),
        "cleanup": "confirmed"
        if cleanup is not None and confirmed(str(cleanup[0]))
        else "unconfirmed",
        "budget": budget(db, "run", identity),
    }


def run_details(db: sqlite3.Connection, row: sqlite3.Row, current_month: str) -> JsonObject:
    value = run_summary(db, row)
    identity = str(row["run_id"])
    counts = db.execute(
        "SELECT state,count(*) FROM managed_calls WHERE run_id=? GROUP BY state", (identity,)
    ).fetchall()
    value["calls"] = {str(item[0]): int(item[1]) for item in counts}
    value["session_budget"] = budget(db, "session", str(row["session_id"]))
    value["admission_month_budget"] = budget(db, "month", str(row["month_id"]))
    value["current_month_id"] = current_month
    return value
