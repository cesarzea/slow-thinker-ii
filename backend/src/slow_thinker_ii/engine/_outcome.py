"""How a run ended: its stop reason, status, detail, results and counts."""

from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.contracts import JsonValue

StopReason = Literal[
    "activation_limit",
    "time_limit",
    "budget_run",
    "budget_day",
    "budget_month",
    "activation_failed",
    "cancelled",
    "internal_error",
]
RunStatus = Literal["completed", "stopped", "failed", "cancelled"]


@dataclass(frozen=True)
class RunResult:
    """A payload received by an Output node, named after that node."""

    node_id: str
    name: str
    message_id: str
    payload: JsonValue


@dataclass(frozen=True)
class RunOutcome:
    status: RunStatus
    reason: StopReason | None  # None when completed
    detail: str  # English; empty when completed
    results: tuple[RunResult, ...]  # in order of arrival
    activations: int  # activations started, including Trigger and Output
    messages: int  # messages sent


@dataclass(frozen=True)
class StopCause:
    reason: StopReason
    detail: str


def status_of(reason: StopReason | None) -> RunStatus:
    if reason is None:
        return "completed"
    if reason in ("activation_failed", "internal_error"):
        return "failed"
    return "cancelled" if reason == "cancelled" else "stopped"


def time_limit_detail(seconds: int) -> str:
    return f"The run reached its time limit of {seconds} seconds."


def failure_detail(node_name: str, number: int, message: str) -> str:
    """`<Node name> activation <n> failed: <cause>`, the cause starting in lower case."""
    first = message[:1]
    lowered = first.lower() + message[1:] if message[1:2].islower() else message
    return f"{node_name} activation {number} failed: {lowered}"
