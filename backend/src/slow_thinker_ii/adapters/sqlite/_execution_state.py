"""Read activation and communication state at a fixed durable event boundary."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, decode_json, json_object


def call_state(db: sqlite3.Connection, run: str, call: str, through: int) -> str:
    row = db.execute(
        "SELECT event,payload_json FROM run_events WHERE run_id=? AND call_id=? AND sequence<=? "
        "AND event IN "
        "('call.dispatch_authorized','call.finished','call.cancel_requested',"
        "'call.cancelled','call.interrupted') "
        "ORDER BY sequence DESC LIMIT 1",
        (run, call, through),
    ).fetchone()
    if row is None:
        return "reserved"
    event = str(row["event"])
    if event == "call.finished":
        return (
            "completed"
            if json_object(decode_json(str(row["payload_json"]))).get("published") is True
            else "failed"
        )
    if event == "call.dispatch_authorized":
        return "dispatched"
    disposition = decode_json(str(row["payload_json"]))
    return (
        "interrupted"
        if event == "call.interrupted" or disposition == "interrupted"
        else "cancelled"
    )


def activation_view(db: sqlite3.Connection, run: str, row: sqlite3.Row, through: int) -> JsonObject:
    context = json_object(decode_json(str(row["context_json"])))
    target = json_object(context["target"])
    selected = db.execute(
        "SELECT json_extract(payload_json,'$.selected_port') FROM run_events "
        "WHERE run_id=? AND call_id=? AND event='activation.routed' AND sequence<=? "
        "ORDER BY sequence DESC LIMIT 1",
        (run, row["call_id"], through),
    ).fetchone()
    ordinal = db.execute(
        "SELECT COUNT(*) FROM run_events e JOIN managed_calls c USING(call_id) "
        "WHERE e.run_id=? AND e.event='call.requested' AND e.sequence<=? AND "
        "c.parent_call_id IS NULL "
        "AND json_extract(c.context_json,'$.activation_id') IS NOT NULL",
        (run, row["sequence"]),
    ).fetchone()[0]
    return {
        "id": context["activation_id"],
        "node": context.get("node_id"),
        "component": target["instance"],
        "ordinal": int(ordinal),
        "state": call_state(db, run, str(row["call_id"]), through),
        "call_id": str(row["call_id"]),
        "selected_port": None if selected is None else str(selected[0]),
    }


def communication_view(
    db: sqlite3.Connection, run: str, row: sqlite3.Row, through: int
) -> JsonObject:
    context = json_object(decode_json(str(row["context_json"])))
    target = json_object(context["target"])
    return {
        "id": str(row["call_id"]),
        "caller": context["caller"] or "platform",
        "target": target["instance"],
        "operation": target["operation"],
        "parent_call_id": context["parent_call_id"],
        "activation_id": context["activation_id"],
        "state": call_state(db, run, str(row["call_id"]), through),
    }
