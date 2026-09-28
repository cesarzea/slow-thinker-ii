"""Usage settlement and overrun detection stay inside the result transaction."""

import sqlite3

from slow_thinker_ii.accounting import ScopeKeys, SettlementOutcome
from slow_thinker_ii.application import CallReceipt, StoredCall

from ._ledger import SqliteLedgerTransaction
from ._rows import attempt, text


def settle_receipt(
    connection: sqlite3.Connection,
    call: StoredCall,
    receipt: CallReceipt,
) -> tuple[SettlementOutcome | None, bool]:
    if receipt.amount is None:
        return None, False
    if receipt.source is None:
        raise ValueError("Settlement source is required")
    ledger = SqliteLedgerTransaction(connection)
    outcome = ledger.settle(call.prepared.context.attempt_id, receipt.amount, receipt.source)
    row = attempt(connection, call.prepared.context.attempt_id)
    scopes = ledger.scopes(
        ScopeKeys(text(row, "run_id"), text(row, "session_id"), text(row, "month_id"))
    )
    overrun = any(scope.settled + scope.outstanding > scope.cap for scope in scopes)
    return outcome, overrun
