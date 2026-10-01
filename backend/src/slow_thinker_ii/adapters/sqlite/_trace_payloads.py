"""Resolve only retained database payloads; every lookup is constrained to its run."""

import sqlite3

from slow_thinker_ii.contracts import JsonObject, decode_json

from ._receipt_rows import RECEIPT
from ._run_rows import CHARGE
from ._trace_bindings import binding_payload, run_input_payload
from ._trace_reports import report_payload


def payload_details(db: sqlite3.Connection, run: str, identity: str) -> JsonObject | None:
    kind, separator, key = identity.partition(":")
    if not separator or not key:
        return None
    if kind == "report":
        return captured_report(db, run, identity, key)
    if kind == "bindings":
        value = binding_payload(db, run, key)
        return None if value is None else captured(run, identity, value)
    if kind == "run-input" and key == run:
        found, value = run_input_payload(db, run)
        return captured(run, identity, value) if found else None
    if kind == "event":
        return event_payload(db, run, identity, key)
    if kind in ("request", "pricing"):
        return call_payload(db, run, identity, kind, key)
    if kind in ("response", "usage"):
        return receipt_payload(db, run, identity, kind, key)
    return None


def call_payload(
    db: sqlite3.Connection, run: str, identity: str, kind: str, key: str
) -> JsonObject | None:
    row = db.execute(
        "SELECT request_json,charge_json FROM managed_calls WHERE run_id=? AND call_id=?",
        (run, key),
    ).fetchone()
    if row is None:
        return None
    value = str(row["request_json"])
    if kind == "pricing":
        value = (
            None
            if row["charge_json"] is None
            else CHARGE.validate_json(str(row["charge_json"])).pricing_json
        )
    return captured(run, identity, value)


def receipt_payload(
    db: sqlite3.Connection, run: str, identity: str, kind: str, key: str
) -> JsonObject | None:
    row = db.execute(
        "SELECT r.receipt_json FROM call_receipts r JOIN managed_calls c USING(call_id) "
        "WHERE c.run_id=? AND r.receipt_id=?",
        (run, key),
    ).fetchone()
    if row is None:
        return None
    receipt = RECEIPT.validate_json(str(row[0]))
    return captured(
        run, identity, receipt.response_json if kind == "response" else receipt.usage_json
    )


def captured(run: str, identity: str, value: str | None) -> JsonObject:
    return {
        "schema_version": "0.1-draft",
        "run_id": run,
        "payload_id": identity,
        "media_type": "application/json",
        "status": "unavailable" if value is None else "present",
        "reason": "not_recorded" if value is None else None,
        "size_bytes": None if value is None else len(value.encode("utf-8")),
        "content": None if value is None else decode_json(value),
    }


def captured_report(db: sqlite3.Connection, run: str, identity: str, key: str) -> JsonObject | None:
    report = report_payload(db, run, key)
    if report is None:
        return None
    result = captured(run, identity, report[0])
    result["status"] = report[1]
    result["reason"] = "authentication_material" if report[1] == "redacted" else None
    return result


def event_payload(db: sqlite3.Connection, run: str, identity: str, key: str) -> JsonObject | None:
    if not key.isascii() or not key.isdecimal() or len(key) > 19 or int(key) > 2**63 - 1:
        return None
    row = db.execute(
        "SELECT payload_json FROM run_events WHERE run_id=? AND sequence=?", (run, int(key))
    ).fetchone()
    return None if row is None else captured(run, identity, str(row[0]))
