"""Real command/run stores with controlled preparation and business operations."""

import asyncio
from collections.abc import AsyncIterator, Callable, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from slow_thinker_ii.access import AccessPolicy, OperationAddress
from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import (
    ExecutionCoordinator,
    ManagedCalls,
    ModelBinding,
    OperationPort,
    PreparationRejected,
    PreparedStart,
    PreparedWorkflow,
    RunEnvironment,
    RunProgram,
    StartIntent,
)

from .managed_calls import FixtureOperation, RealClock
from .operator_commands import OperatorCase, operator_case

TARGET = OperationAddress("worker", "run")


class Environment:
    def __init__(self, operation: FixtureOperation) -> None:
        self.operation, self.opened, self.closed = operation, 0, 0

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        assert deadline > 0
        self.opened += 1
        try:
            yield {TARGET: self.operation}
        finally:
            self.closed += 1

    def report(self) -> str:
        return "[]"


class Program:
    async def execute(self, calls: ManagedCalls) -> str:
        result = await calls.schedule(TARGET, "{}")
        return result.result.payload_json


class Preparer:
    def __init__(self, case: OperatorCase) -> None:
        self.case, self.operation = case, FixtureOperation()
        self.environment: RunEnvironment = Environment(self.operation)
        self.program: RunProgram = Program()
        self.policy = AccessPolicy((TARGET,), (), (TARGET,))
        self.calls: list[StartIntent] = []
        self.entered, self.release, self.cancelled = (
            asyncio.Event(),
            asyncio.Event(),
            asyncio.Event(),
        )
        self.release.set()
        self.failure: PreparationRejected | None = None
        self.models: tuple[ModelBinding, ...] = ()
        self.wrong_identity = False
        self.snapshot_json = "{}"
        self.ignore_cancel = False

    async def prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow:
        self.calls.append(intent)
        self.entered.set()
        try:
            await self.release.wait()
        except asyncio.CancelledError:
            self.cancelled.set()
            if not self.ignore_cancel:
                raise
            await self.release.wait()
        if self.failure is not None:
            raise self.failure
        prepared = PreparedStart(
            intent,
            self.case.profile,
            "wrong" if self.wrong_identity else runtime_id,
            self.snapshot_json,
        )
        return PreparedWorkflow(prepared, self.policy, self.environment, self.program, self.models)


@dataclass(frozen=True)
class CoordinatorCase:
    base: OperatorCase
    commands: SqliteOperatorStore
    runs: SqliteRunStore
    preparer: Preparer
    coordinator: ExecutionCoordinator


def coordinator_case(
    directory: Path,
    *,
    preparation: float = 5,
    shutdown: float = 2,
    maximum: int = 4,
    clock: RealClock | None = None,
) -> CoordinatorCase:
    base = operator_case(directory)
    clock = RealClock() if clock is None else clock
    commands = SqliteOperatorStore(base.database, 1_048_576, clock, base.wall)
    runs = SqliteRunStore(base.database, 1_048_576, base.wall)
    preparer = Preparer(base)
    coordinator = ExecutionCoordinator(
        commands, runs, preparer, clock, preparation, shutdown, maximum
    )
    return CoordinatorCase(base, commands, runs, preparer, coordinator)


async def eventually(condition: Callable[[], bool]) -> None:
    async with asyncio.timeout(5):
        while not condition():
            await asyncio.sleep(0.005)
