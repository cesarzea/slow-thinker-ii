"""Typed operation preparation and transport ports keep provider SDKs outside use cases."""

from dataclasses import dataclass
from typing import Protocol

from slow_thinker_ii.access import CallContext
from slow_thinker_ii.contracts import OperationResult

from ._receipts import ReceiptOutcome
from ._run_records import ChargeBasis


@dataclass(frozen=True)
class PreparedOperation:
    arguments_json: str
    charge: ChargeBasis | None


@dataclass(frozen=True)
class ChargeEvidence:
    usage_json: str | None
    amount: int | None
    source: str | None


@dataclass(frozen=True)
class OperationReply:
    result: OperationResult
    charge: ChargeEvidence | None = None


@dataclass(frozen=True)
class ManagedResult:
    context: CallContext
    result: OperationResult
    receipt_id: str
    outcome: ReceiptOutcome


class OperationPort(Protocol):
    def prepare(self, arguments_json: str) -> PreparedOperation: ...
    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply: ...


class PricingPolicy(Protocol):
    def quote(self, arguments_json: str) -> ChargeBasis: ...
    def reconcile(self, result: OperationResult) -> ChargeEvidence: ...
