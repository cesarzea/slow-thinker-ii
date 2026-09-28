"""Trusted result receipts retain native evidence separately from output eligibility."""

from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.accounting import MAX_QUANTA, SettlementOutcome


@dataclass(frozen=True)
class CallReceipt:
    receipt_id: str
    call_id: str
    response_json: str
    succeeded: bool
    usage_json: str | None = None
    amount: int | None = None
    source: str | None = None

    def __post_init__(self) -> None:
        if not self.receipt_id or not self.call_id or type(self.succeeded) is not bool:
            raise ValueError("A receipt requires identities and an explicit outcome")
        if self.amount is not None and (
            type(self.amount) is not int or not 0 <= self.amount <= MAX_QUANTA or not self.source
        ):
            raise ValueError("A settled amount requires valid source evidence")


@dataclass(frozen=True)
class ReceiptOutcome:
    disposition: Literal["recorded", "duplicate", "conflict"]
    publish: bool
    reason: str | None
    settlement: SettlementOutcome | None = None


@dataclass(frozen=True)
class SavedReceipt:
    receipt: CallReceipt
    outcome: ReceiptOutcome
