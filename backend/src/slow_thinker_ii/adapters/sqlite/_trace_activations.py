"""Activation inspection follows stored invocation identity, never participant names."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

from ._operator_cursors import OperatorCursors
from ._trace_reports import activation_reports


def activation_details(
    db: sqlite3.Connection,
    run: str,
    activation: str,
    cursor: str | None,
    cursors: OperatorCursors,
    size: int,
) -> JsonObject | None:
    roots = db.execute(
        "SELECT * FROM managed_calls WHERE run_id=? AND parent_call_id IS NULL "
        "AND json_extract(context_json,'$.activation_id')=? LIMIT 2",
        (run, activation),
    ).fetchall()
    if not roots:
        return None
    if len(roots) != 1:
        raise ValueError("An activation must have one originating call")
    result = activation_summary(roots[0], run, activation)
    result["reports"] = activation_reports(db, run, activation)
    result["calls"] = activation_calls(db, run, activation, cursor, cursors, size)
    return result


def activation_summary(root: sqlite3.Row, run: str, activation: str) -> JsonObject:
    context = json_object(decode_json(str(root["context_json"])))
    return {
        "schema_version": "0.1-draft",
        "run_id": run,
        "activation_id": activation,
        "node_id": context.get("node_id"),
        "target": context["target"],
        "root_call_id": str(root["call_id"]),
        "state": str(root["state"]),
        "reason": root["reason"],
        "input_payload_id": "request:" + str(root["call_id"]),
        "output_payload_id": "response:" + str(root["result_receipt_id"])
        if root["state"] == "completed" and root["result_receipt_id"] is not None
        else None,
        "bindings_payload_id": "bindings:" + str(root["call_id"]),
    }


def activation_calls(
    db: sqlite3.Connection,
    run: str,
    activation: str,
    cursor: str | None,
    cursors: OperatorCursors,
    size: int,
) -> JsonObject:
    scope = "activation:" + run + ":" + activation
    predicate = "run_id=? AND json_extract(context_json,'$.activation_id')=?"
    upper = int(
        db.execute(
            "SELECT COALESCE(MAX(rowid),0) FROM managed_calls WHERE " + predicate,
            (run, activation),
        ).fetchone()[0]
    )
    through, after = (upper, 0) if cursor is None else cursors.decode(cursor, scope)
    rows = db.execute(
        "SELECT rowid AS position,* FROM managed_calls WHERE "
        + predicate
        + " AND rowid>? AND rowid<=? ORDER BY rowid LIMIT ?",
        (run, activation, after, through, size + 1),
    ).fetchall()
    items: list[JsonValue] = [activation_call(row) for row in rows[:size]]
    next_cursor = (
        cursors.encode(scope, through, int(rows[size - 1]["position"]))
        if len(rows) > size
        else None
    )
    return {"items": items, "next_cursor": next_cursor}


def activation_call(row: sqlite3.Row) -> JsonObject:
    context = json_object(decode_json(str(row["context_json"])))
    return {
        "call_id": str(row["call_id"]),
        "parent_call_id": row["parent_call_id"],
        "caller": context["caller"],
        "target": context["target"],
        "state": str(row["state"]),
    }
