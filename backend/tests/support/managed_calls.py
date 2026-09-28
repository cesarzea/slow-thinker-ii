"""Deterministic operation behavior with a real monotonic clock for async deadlines."""

import asyncio
import time

from slow_thinker_ii.application import (
    ChargeBasis,
    ChargeEvidence,
    ManagedCalls,
    ManagedResult,
    OperationReply,
    PreparedOperation,
)
from slow_thinker_ii.contracts import OperationResult

from .authority import REVIEWER, Clock, alias
from .run_admission import RunCase


class RealClock(Clock):
    def __call__(self) -> float:
        return time.monotonic()


class FixtureOperation:
    def __init__(
        self, charge: ChargeBasis | None = None, evidence: ChargeEvidence | None = None
    ) -> None:
        self.charge, self.evidence = charge, evidence
        self.result = OperationResult('{"done":true}', False)
        self.started, self.release = asyncio.Event(), asyncio.Event()
        self.release.set()
        self.reject = False
        self.ignore_cancel = False
        self.error: Exception | None = None
        self.preparation_error: Exception | None = None
        self.calls: list[tuple[str, str, float]] = []

    def prepare(self, arguments_json: str) -> PreparedOperation:
        if self.preparation_error is not None:
            raise self.preparation_error
        if self.reject:
            raise ValueError("Fixture rejected arguments")
        return PreparedOperation(arguments_json, self.charge)

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        self.calls.append((arguments_json, grant, deadline))
        self.started.set()
        try:
            await self.release.wait()
        except asyncio.CancelledError:
            if not self.ignore_cancel:
                raise
            await self.release.wait()
        if self.error is not None:
            raise self.error
        return OperationReply(self.result, self.evidence)


class NestedOperation(FixtureOperation):
    def __init__(self, case: RunCase) -> None:
        super().__init__()
        self.case = case
        self.runner: ManagedCalls | None = None
        self.child: ManagedResult | None = None

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        del deadline
        assert self.runner is not None
        target = alias(self.case.authority, grant, REVIEWER)
        self.child = await self.runner.invoke(grant, target, arguments_json)
        return OperationReply(self.child.result)
