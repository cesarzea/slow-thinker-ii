"""Keep one task per accepted run and route Stop to its current runtime owner."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass

from slow_thinker_ii.access import AccessDenied

from ._dispatch_ports import ManagedResult
from ._gateway_records import GatewayTool
from ._native_records import NativeReply
from ._operator_ports import PreparedWorkflow
from ._run_ports import RunStore
from ._workflow_runtime import WorkflowRuntime, build_runtime, failed_before_launch, read_run


@dataclass
class OwnedWorkflow:
    task: asyncio.Task[None] | None = None
    runtime: WorkflowRuntime | None = None
    stop_reason: str | None = None


class WorkflowOwners:
    def __init__(self, store: RunStore, clock: Callable[[], float]) -> None:
        self._store, self._clock = store, clock
        self._owners: dict[str, OwnedWorkflow] = {}
        self._failures: dict[str, str] = {}

    def launch(self, identity: str, workflow: PreparedWorkflow, *, stopping: bool) -> None:
        if identity in self._owners:
            raise RuntimeError("A run already has an owner")
        owner = OwnedWorkflow(stop_reason="runtime_shutdown" if stopping else None)
        self._owners[identity] = owner
        owner.task = asyncio.create_task(self._execute(identity, workflow, owner))
        owner.task.add_done_callback(lambda task: self._finished(identity, task))

    async def _execute(
        self, identity: str, workflow: PreparedWorkflow, owner: OwnedWorkflow
    ) -> None:
        record = await asyncio.to_thread(read_run, self._store, identity)
        try:
            owner.runtime = build_runtime(workflow, record, self._store, self._clock)
        except Exception:
            await asyncio.to_thread(failed_before_launch, self._store, record, self._clock())
            raise
        if owner.stop_reason is not None:
            owner.runtime.run.stop(owner.stop_reason)
        await owner.runtime.run.execute(workflow.program)

    def _finished(self, identity: str, task: asyncio.Task[None]) -> None:
        self._owners.pop(identity, None)
        if not task.cancelled():
            error = task.exception()
            if error is not None:
                self._failures[identity] = type(error).__name__

    def stop(self, identity: str, reason: str) -> None:
        owner = self._owners.get(identity)
        if owner is not None:
            owner.stop_reason = owner.stop_reason or reason
            if owner.runtime is not None:
                owner.runtime.run.stop(owner.stop_reason)

    def stop_all(self, reason: str) -> None:
        for identity in tuple(self._owners):
            try:
                self.stop(identity, reason)
            except Exception as error:
                self._failures[identity] = type(error).__name__

    def pending(self) -> tuple[str, ...]:
        return tuple(self._owners)

    def failures(self) -> tuple[tuple[str, str], ...]:
        return tuple(self._failures.items())

    def tasks(self) -> tuple[asyncio.Task[None], ...]:
        return tuple(owner.task for owner in self._owners.values() if owner.task is not None)

    def _gateway(self, grant: str) -> WorkflowRuntime:
        for owner in self._owners.values():
            if owner.runtime is not None:
                try:
                    owner.runtime.gateway.deadline(grant)
                except AccessDenied:
                    continue
                return owner.runtime
        raise AccessDenied("run_closed")

    def deadline(self, grant: str) -> float:
        return self._gateway(grant).gateway.deadline(grant)

    async def complete(self, grant: str, request_json: str) -> NativeReply:
        return await self._gateway(grant).gateway.complete(grant, request_json)

    def tools(self, grant: str) -> tuple[GatewayTool, ...]:
        return self._gateway(grant).components.tools(grant)

    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult:
        return await self._gateway(grant).components.invoke(grant, alias, arguments_json)

    def report(self, grant: str, report_json: str) -> None:
        self._gateway(grant).components.report(grant, report_json)

    def reject(self, grant: str, requested_operation: str, reason: str) -> None:
        try:
            self._gateway(grant).components.reject(grant, requested_operation, reason)
        except AccessDenied:
            return
