"""Checks applied inside the same admission transaction as the call snapshot."""

from slow_thinker_ii.access import AccessDenied, CallContext

from ._run_records import RunRecord


def validate_context(context: CallContext, run: RunRecord, now: float) -> None:
    if context.run_id != run.run_id or context.graph_revision != run.graph_revision:
        raise AccessDenied("run_context_mismatch")
    if context.deadline > run.deadline or now >= context.deadline:
        raise AccessDenied("call_deadline")
