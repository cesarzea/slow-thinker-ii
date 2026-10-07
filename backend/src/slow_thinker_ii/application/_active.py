"""Active runs: their plan, journal, engine and hosts, call deadlines and in-flight model calls."""

import asyncio
from contextlib import suppress
from dataclasses import dataclass

from slow_thinker_ii import engine
from slow_thinker_ii.access import Caller, Grants
from slow_thinker_ii.graphs import PlanComponent, RunPlan

from ._journal import RunJournal
from ._ports import RunHosts
from ._values import ProviderReply

SETTLE_SECONDS = 5.0  # longest wait for in-flight model calls to be recorded at the run's end


class CallGrants:
    """The engine's grant issuer for one run: real grants, plus the deadline of each caller."""

    def __init__(self, grants: Grants, clock: engine.Clock) -> None:
        self._grants = grants
        self._clock = clock
        self._deadlines: dict[Caller, float] = {}

    def issue(self, caller: Caller, ttl_seconds: float) -> str:
        token = self._grants.issue(caller, ttl_seconds)
        self._deadlines[caller] = self._clock.monotonic() + ttl_seconds
        return token

    def revoke(self, token: str) -> None:
        self._grants.revoke(token)

    def remaining(self, caller: Caller) -> float:
        """Seconds left in the caller's current call; the latest grant of a caller wins."""
        now = self._clock.monotonic()
        return self._deadlines.get(caller, now) - now


class ActiveRun:
    """A run from admission until its background task ends."""

    def __init__(self, run_id: str, plan: RunPlan, journal: RunJournal, grants: CallGrants) -> None:
        self.run_id = run_id
        self.plan = plan
        self.journal = journal
        self.grants = grants
        self.hosts: RunHosts | None = None
        self.task: asyncio.Task[None] | None = None
        self._engine: engine.RunEngine | None = None
        self._pending: tuple[engine.StopReason, str] | None = None
        self._provider_calls: set[asyncio.Task[ProviderReply]] = set()
        self._in_flight = 0
        self._idle = asyncio.Event()
        self._idle.set()

    def status(self) -> str:
        return "running" if self.journal.running else "starting"

    def attach(self, run_engine: engine.RunEngine) -> None:
        """Hands over the engine, applying a stop requested while the hosts were starting."""
        self._engine = run_engine
        if self._pending is not None:
            run_engine.stop(*self._pending)

    def stop(self, reason: engine.StopReason, detail: str) -> None:
        if self._engine is not None:
            self._engine.stop(reason, detail)
        elif self._pending is None:
            self._pending = (reason, detail)

    def begin_call(self) -> None:
        self._in_flight += 1
        self._idle.clear()

    def end_call(self) -> None:
        self._in_flight -= 1
        if self._in_flight == 0:
            self._idle.set()

    def watch(self, call: asyncio.Task[ProviderReply]) -> None:
        self._provider_calls.add(call)

    def unwatch(self, call: asyncio.Task[ProviderReply]) -> None:
        self._provider_calls.discard(call)

    async def settle_calls(self) -> None:
        """Cancels provider calls still running and waits until every call is recorded."""
        for call in list(self._provider_calls):
            call.cancel()
        with suppress(TimeoutError):
            await asyncio.wait_for(self._idle.wait(), SETTLE_SECONDS)


@dataclass(frozen=True)
class ActiveCall:
    """The resolved caller of a grant: its run, plan component and remaining call time."""

    caller: Caller
    component: PlanComponent
    run: ActiveRun
    remaining_seconds: float


def caller_component(plan: RunPlan, caller: Caller) -> PlanComponent:
    node = plan.node(caller.node_id)
    if caller.position == "memory" and node.embedded_memory is not None:
        return node.embedded_memory
    embedded = node.embedded_output
    return embedded if caller.position == "output" and embedded is not None else node.host
