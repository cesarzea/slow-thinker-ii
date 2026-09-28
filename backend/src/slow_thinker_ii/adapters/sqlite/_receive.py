"""Commit response evidence, charge settlement and eligible output as one unit."""

import json
import sqlite3

from slow_thinker_ii.access import InvocationEnd
from slow_thinker_ii.application import CallReceipt, ReceiptOutcome

from ._receipt_completion import complete_call, completion_reason
from ._receipt_money import settle_receipt
from ._receipt_rows import insert_receipt
from ._run_events import append_event
from ._run_rows import read_call, read_run
from ._run_stop import cancel_tree, stop_run


def receive(
    connection: sqlite3.Connection,
    receipt: CallReceipt,
    gate: InvocationEnd,
    now: float,
    runtime_id: str,
    limit: int,
) -> ReceiptOutcome:
    call = read_call(connection, receipt.call_id)
    run = read_run(connection, call.prepared.context.run_id)
    reason = completion_reason(connection, call, run, gate, now, runtime_id)
    if reason is None and not receipt.succeeded:
        reason = "operation_failed"
    settlement, overrun = settle_receipt(connection, call, receipt)
    if overrun:
        reason = "budget_overrun"
    outcome = ReceiptOutcome("recorded", reason is None, reason, settlement)
    insert_receipt(connection, receipt, outcome)
    complete_call(connection, call, receipt.receipt_id, reason)
    record_events(connection, run.run_id, receipt, outcome, call.state == "dispatched", limit)
    if reason == "unfinished_children":
        cancel_tree(connection, receipt.call_id, limit)
    if reason in ("deadline_expired", "budget_overrun", "authority_closed"):
        stop_run(connection, run.run_id, reason, "stopping", limit)
    return outcome


def record_events(
    connection: sqlite3.Connection,
    run_id: str,
    receipt: CallReceipt,
    outcome: ReceiptOutcome,
    finished: bool,
    limit: int,
) -> None:
    payload = json.dumps(
        {
            "receipt_id": receipt.receipt_id,
            "published": outcome.publish,
            "reason": outcome.reason,
            "settlement": outcome.settlement,
            "late": not finished
            or outcome.reason in ("run_closed", "deadline_expired", "authority_closed"),
        }
    )
    append_event(connection, run_id, "call.response_received", receipt.call_id, payload, limit)
    if receipt.usage_json is not None:
        append_event(connection, run_id, "usage.recorded", receipt.call_id, payload, limit)
    if outcome.settlement is not None:
        append_event(connection, run_id, "accounting.changed", receipt.call_id, payload, limit)
    if finished:
        append_event(connection, run_id, "call.finished", receipt.call_id, payload, limit)
