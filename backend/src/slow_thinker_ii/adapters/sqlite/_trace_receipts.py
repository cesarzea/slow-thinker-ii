"""Receipt pages keep late responses and publication eligibility distinct."""

import sqlite3

from slow_thinker_ii.accounting import display_amount
from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._operator_cursors import OperatorCursors
from ._receipt_rows import OUTCOME, RECEIPT


def receipt_page(
    db: sqlite3.Connection,
    run: str,
    call: str,
    cursor: str | None,
    cursors: OperatorCursors,
    size: int,
) -> JsonObject:
    scope = "receipts:" + run + ":" + call
    upper = int(
        db.execute(
            "SELECT COALESCE(MAX(rowid),0) FROM call_receipts WHERE call_id=?", (call,)
        ).fetchone()[0]
    )
    through, after = (upper, 0) if cursor is None else cursors.decode(cursor, scope)
    rows = db.execute(
        "SELECT rowid AS position,* FROM call_receipts WHERE call_id=? AND rowid>? "
        "AND rowid<=? ORDER BY rowid LIMIT ?",
        (call, after, through, size + 1),
    ).fetchall()
    items: list[JsonValue] = [receipt_item(row) for row in rows[:size]]
    next_cursor = (
        cursors.encode(scope, through, int(rows[size - 1]["position"]))
        if len(rows) > size
        else None
    )
    return {"items": items, "next_cursor": next_cursor}


def receipt_item(row: sqlite3.Row) -> JsonObject:
    receipt = RECEIPT.validate_json(str(row["receipt_json"]))
    outcome = OUTCOME.validate_json(str(row["outcome_json"]))
    return {
        "receipt_id": receipt.receipt_id,
        "received_at": str(row["received_at"]),
        "succeeded": receipt.succeeded,
        "publish": outcome.publish,
        "reason": outcome.reason,
        "response_payload_id": "response:" + receipt.receipt_id,
        "usage_payload_id": "usage:" + receipt.receipt_id,
        "currency": "USD",
        "amount": None if receipt.amount is None else display_amount(receipt.amount),
        "source": receipt.source,
    }
