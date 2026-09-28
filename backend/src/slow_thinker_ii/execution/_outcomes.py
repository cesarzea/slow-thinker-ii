"""Initial execution outcomes follow the first durably accepted stop cause."""

from typing import Literal

type RunState = Literal[
    "created", "running", "stopping", "completed", "failed", "cancelled", "timed_out", "interrupted"
]
type TerminalState = Literal["completed", "failed", "cancelled", "timed_out", "interrupted"]


def stopped_outcome(reason: str | None) -> TerminalState:
    if reason in ("run_deadline", "call_deadline", "deadline_expired"):
        return "timed_out"
    if reason in ("operator_stop", "control_stop", "runtime_shutdown"):
        return "cancelled"
    return "failed"
