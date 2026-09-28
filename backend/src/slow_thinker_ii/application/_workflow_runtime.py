"""Construct transient authority only for a newly admitted workflow."""

from collections.abc import Callable
from dataclasses import dataclass

from slow_thinker_ii.access import CallAuthority, CallLimits
from slow_thinker_ii.contracts import encode_json

from ._managed_run import ManagedRun
from ._native_gateway import NativeModelGateway
from ._operator_ports import PreparedWorkflow
from ._run_admission import RunAdmission
from ._run_finalization import RunFinalization
from ._run_ports import RunStore
from ._run_records import RunRecord


@dataclass(frozen=True)
class WorkflowRuntime:
    run: ManagedRun
    gateway: NativeModelGateway


def read_run(store: RunStore, identity: str) -> RunRecord:
    with store.begin() as transaction:
        return transaction.run(identity)


def build_runtime(
    workflow: PreparedWorkflow, record: RunRecord, store: RunStore, clock: Callable[[], float]
) -> WorkflowRuntime:
    limits = workflow.start.configuration.limits
    authority = CallAuthority(
        record.run_id,
        record.graph_revision,
        workflow.policy,
        CallLimits(limits.max_calls, limits.max_depth, limits.call_seconds),
        record.deadline,
        clock,
    )
    admission = RunAdmission(authority, store, record.run_id, record.runtime_id, clock)
    finish = RunFinalization(authority, store, record.run_id, record.runtime_id, clock)
    runtime = ManagedRun(
        authority, admission, finish, workflow.environment, record.deadline, limits.shutdown_seconds
    )
    return WorkflowRuntime(runtime, NativeModelGateway(authority, runtime, workflow.models))


def failed_before_launch(store: RunStore, record: RunRecord, now: float) -> None:
    reason = "run_deadline" if now >= record.deadline else "startup_failure"
    with store.begin() as transaction:
        transaction.stop(record.run_id, reason)
        transaction.finish_run(record.run_id, record.runtime_id, now, None, executing=False)
        transaction.event(
            record.run_id,
            "run.cleanup",
            None,
            encode_json(
                {
                    "environment_json": "[]",
                    "pending_calls": [],
                    "error_type": "runtime_construction",
                }
            ),
        )
