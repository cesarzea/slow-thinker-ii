"""Validate and retain exact receipts; duplicate identity never replaces evidence."""

import json
import sqlite3

from pydantic import TypeAdapter

from slow_thinker_ii.application import CallReceipt, ReceiptOutcome, SavedReceipt, StoredCall

from ._rows import text
from ._run_events import append_event
from ._run_rows import bounded_json, read_call

RECEIPT = TypeAdapter(CallReceipt)
OUTCOME = TypeAdapter(ReceiptOutcome)


def read_receipt(connection: sqlite3.Connection, receipt_id: str) -> SavedReceipt | None:
    row = connection.execute(
        "SELECT * FROM call_receipts WHERE receipt_id=?", (receipt_id,)
    ).fetchone()
    if row is None:
        return None
    return SavedReceipt(
        RECEIPT.validate_json(text(row, "receipt_json")),
        OUTCOME.validate_json(text(row, "outcome_json")),
    )


def check_receipt(
    connection: sqlite3.Connection, receipt: CallReceipt, limit: int
) -> ReceiptOutcome | None:
    call = validate_receipt(connection, receipt, limit)
    previous = read_receipt(connection, receipt.receipt_id)
    if previous is None:
        return None
    if previous.receipt == receipt:
        return ReceiptOutcome(
            "duplicate", False, previous.outcome.reason, previous.outcome.settlement
        )
    payload = json.dumps({"conflict": True, "receipt": RECEIPT.dump_python(receipt, mode="json")})
    append_event(
        connection,
        call.prepared.context.run_id,
        "call.response_received",
        receipt.call_id,
        payload,
        limit,
    )
    return ReceiptOutcome("conflict", False, "receipt_conflict")


def validate_receipt(
    connection: sqlite3.Connection, receipt: CallReceipt, limit: int
) -> StoredCall:
    call = read_call(connection, receipt.call_id)
    bounded_json(connection, receipt.response_json, limit)
    bounded_json(connection, RECEIPT.dump_json(receipt).decode(), limit)
    if receipt.usage_json is not None:
        bounded_json(connection, receipt.usage_json, limit)
    if receipt.amount is not None and call.prepared.charge is None:
        raise ValueError("An unbilled call cannot receive a charge")
    authorized = connection.execute(
        "SELECT 1 FROM run_events WHERE call_id=? AND event='call.dispatch_authorized' LIMIT 1",
        (receipt.call_id,),
    ).fetchone()
    if authorized is None:
        raise ValueError("A response requires a prior dispatch authorization")
    return call


def insert_receipt(
    connection: sqlite3.Connection, receipt: CallReceipt, outcome: ReceiptOutcome
) -> None:
    connection.execute(
        "INSERT INTO call_receipts(receipt_id,call_id,receipt_json,outcome_json) VALUES(?,?,?,?)",
        (
            receipt.receipt_id,
            receipt.call_id,
            RECEIPT.dump_json(receipt).decode(),
            OUTCOME.dump_json(outcome).decode(),
        ),
    )
