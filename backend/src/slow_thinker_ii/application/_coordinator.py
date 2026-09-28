"""Own commands independently of their HTTP waiters and hand each new receipt to one run task."""

import asyncio
import math
from collections.abc import Callable
from uuid import uuid4

from ._command_jobs import CommandJobs
from ._native_records import NativeModelService
from ._operator_ports import (
    CoordinatorShutdown,
    CoordinatorUnavailable,
    OperatorCommandStore,
    PreparationRejected,
    WorkflowPreparer,
)
from ._operator_records import CommandResult, StartIntent
from ._preparation_tasks import PreparationTasks
from ._run_ports import RecordingError, RunStore
from ._workflow_owners import WorkflowOwners


class ExecutionCoordinator:
    def __init__(
        self,
        commands: OperatorCommandStore,
        runs: RunStore,
        preparer: WorkflowPreparer,
        clock: Callable[[], float],
        preparation_seconds: float,
        shutdown_seconds: float,
        maximum_commands: int,
    ) -> None:
        if any(
            isinstance(value, bool) or not math.isfinite(value) or value <= 0
            for value in (preparation_seconds, shutdown_seconds)
        ):
            raise ValueError("Finite preparation and shutdown bounds are required")
        if type(maximum_commands) is not int or maximum_commands < 1:
            raise ValueError("A positive pending-command bound is required")
        self._store, self._shutdown = commands, shutdown_seconds
        self._runtime, self._closing = uuid4().hex, False
        self._jobs = CommandJobs(maximum_commands)
        self._controls = CommandJobs(maximum_commands)
        self._preparation = PreparationTasks(preparer, preparation_seconds, maximum_commands)
        self._owners = WorkflowOwners(runs, clock)

    def _require_open(self) -> None:
        if self._closing:
            raise CoordinatorUnavailable("backend_stopping")

    async def start(self, command_id: str, intent: StartIntent) -> CommandResult:
        self._require_open()
        return await self._jobs.submit(
            f"start:{command_id}", intent.to_json(), lambda: self._start(command_id, intent)
        )

    async def _start(self, command_id: str, intent: StartIntent) -> CommandResult:
        known = await asyncio.to_thread(self._store.resolve, command_id, intent)
        if known is not None:
            return known
        try:
            self._require_open()
            workflow = await self._preparation.prepare(command_id, intent, self._runtime)
            workflow.require_identity(intent, self._runtime)
            self._require_open()
        except (PreparationRejected, CoordinatorUnavailable) as error:
            reason = error.code if isinstance(error, PreparationRejected) else "backend_stopping"
            return await asyncio.to_thread(self._store.reject, command_id, intent, reason)
        result = await asyncio.to_thread(self._store.admit, command_id, workflow.start)
        receipt = result.receipt
        if not result.replayed and receipt.disposition == "accepted":
            assert receipt.target_id is not None
            self._owners.launch(receipt.target_id, workflow, stopping=self._closing)
        return result

    async def create_session(self, command_id: str, name: str) -> CommandResult:
        self._require_open()
        return await self._controls.submit(
            f"session:{command_id}",
            name,
            lambda: asyncio.to_thread(self._store.create_session, command_id, name),
        )

    async def stop(self, command_id: str, run_id: str) -> CommandResult:
        self._require_open()
        return await self._controls.submit(
            f"stop:{command_id}", run_id, lambda: self._stop(command_id, run_id)
        )

    async def _stop(self, command_id: str, run_id: str) -> CommandResult:
        try:
            result = await asyncio.to_thread(self._store.stop, command_id, run_id)
        except RecordingError:
            self._owners.stop_all("recording_failure")
            raise
        if result.receipt.disposition == "accepted":
            self._owners.stop(run_id, result.receipt.reason or "operator_stop")
        return result

    async def withdraw(self, command_id: str) -> CommandResult:
        self._require_open()
        return await self._controls.submit(
            f"withdraw:{command_id}", "{}", lambda: self._withdraw(command_id)
        )

    async def _withdraw(self, command_id: str) -> CommandResult:
        try:
            result = await asyncio.to_thread(self._store.withdraw, command_id)
        except RecordingError:
            self._owners.stop_all("recording_failure")
            raise
        if result.receipt.target_id is not None:
            self._owners.stop(result.receipt.target_id, result.receipt.reason or "operator_stop")
        return result

    async def close(self) -> CoordinatorShutdown:
        self._closing = True
        self._preparation.cancel()
        self._owners.stop_all("runtime_shutdown")
        deadline = asyncio.get_running_loop().time() + self._shutdown
        while tasks := (
            *self._jobs.tasks(),
            *self._controls.tasks(),
            *self._preparation.tasks(),
            *self._owners.tasks(),
        ):
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                break
            await asyncio.wait(tasks, timeout=remaining, return_when=asyncio.FIRST_COMPLETED)
        return self.pending()

    def pending(self) -> CoordinatorShutdown:
        return CoordinatorShutdown(
            (*self._jobs.pending(), *self._controls.pending()),
            self._preparation.pending(),
            self._owners.pending(),
        )

    @property
    def gateway(self) -> NativeModelService:
        return self._owners

    def failures(self) -> tuple[tuple[str, str], ...]:
        return self._owners.failures()
