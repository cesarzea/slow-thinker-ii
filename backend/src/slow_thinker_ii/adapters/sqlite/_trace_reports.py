"""Expose bounded optional reports as captured payload references with reported provenance."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object


def reports(db: sqlite3.Connection, run: str, call: str) -> list[JsonValue]:
    rows = db.execute(
        "SELECT sequence,payload_json FROM run_events WHERE run_id=? AND call_id=? "
        "AND event='component.reported' ORDER BY sequence LIMIT 101",
        (run, call),
    ).fetchall()
    if len(rows) > 100:
        raise ValueError("Recorded report count exceeded its admission bound")
    return [report_item(row) for row in rows]


def activation_reports(db: sqlite3.Connection, run: str, activation: str) -> list[JsonValue]:
    rows = db.execute(
        "SELECT sequence,payload_json FROM run_events WHERE run_id=? "
        "AND event='component.reported' AND json_extract(payload_json,'$.activation_id')=? "
        "ORDER BY sequence LIMIT 101",
        (run, activation),
    ).fetchall()
    if len(rows) > 100:
        raise ValueError("Recorded activation report count exceeded its admission bound")
    return [report_item(row) for row in rows]


def report_item(row: sqlite3.Row) -> JsonObject:
    value = json_object(decode_json(str(row["payload_json"])))
    return {
        "event_sequence": int(row["sequence"]),
        "kind": value["kind"],
        "schema_version": value["schema_version"],
        "evidence": "reported",
        "payload_id": "report:" + str(row["sequence"]),
        "source_occurred_at": value.get("source_occurred_at"),
    }


def report_payload(db: sqlite3.Connection, run: str, key: str) -> tuple[str, str] | None:
    if not key.isascii() or not key.isdecimal() or len(key) > 19 or int(key) > 2**63 - 1:
        return None
    row = db.execute(
        "SELECT payload_json FROM run_events WHERE run_id=? AND sequence=? "
        "AND event='component.reported'",
        (run, int(key)),
    ).fetchone()
    if row is None:
        return None
    value = json_object(decode_json(str(row[0])))
    return encode_json(value["value"]), str(value["capture_status"])
