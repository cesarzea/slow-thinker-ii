"""Usage settlement and overrun detection stay inside the result transaction."""

import sqlite3

from slow_thinker_ii.accounting import ScopeKeys, SettlementOutcome
from slow_thinker_ii.application import CallReceipt, StoredCall

from ._ledger import SqliteLedgerTransaction
from ._pricing_quarantine import quarantine
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
    above_bound = receipt.amount > int(row["bound"])
    if above_bound and outcome == "applied":
        quarantine(connection, call.prepared, receipt.amount)
    overrun = above_bound or any(scope.settled + scope.outstanding > scope.cap for scope in scopes)
    return outcome, overrun
