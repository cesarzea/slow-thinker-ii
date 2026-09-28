"""Durable run and call records never contain invocation credentials."""

import math
from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.access import CallContext
from slow_thinker_ii.accounting import MAX_QUANTA
from slow_thinker_ii.execution import RunState as RunState

type CallState = Literal[
    "reserved", "dispatched", "completed", "failed", "cancelled", "interrupted"
]


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    graph_revision: str
    session_id: str
    month_id: str
    runtime_id: str
    deadline: float
    snapshot_json: str
    state: RunState = "created"
    reason: str | None = None

    def __post_init__(self) -> None:
        if not all(
            (self.run_id, self.graph_revision, self.session_id, self.month_id, self.runtime_id)
        ):
            raise ValueError("Run and scope identities are required")
        if isinstance(self.deadline, bool) or not math.isfinite(self.deadline):
            raise ValueError("A finite runtime deadline is required")


@dataclass(frozen=True)
class ChargeBasis:
    bound: int
    tariff_revision: str
    pricing_json: str

    def __post_init__(self) -> None:
        if (
            type(self.bound) is not int
            or not 0 <= self.bound <= MAX_QUANTA
            or not self.tariff_revision
        ):
            raise ValueError("A charge requires a bounded amount and tariff identity")


@dataclass(frozen=True)
class PreparedCall:
    context: CallContext
    request_json: str
    charge: ChargeBasis | None


@dataclass(frozen=True)
class StoredCall:
    prepared: PreparedCall
    state: CallState


@dataclass(frozen=True)
class RunEvent:
    sequence: int
    event: str
    call_id: str | None
    payload_json: str
