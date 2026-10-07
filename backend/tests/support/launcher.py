"""A `HostLauncher` that serves scripted hosts and records host readiness like the real one."""

from collections.abc import Callable

from slow_thinker_ii.application import StartupFailed
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission, Hosts, RunLog
from slow_thinker_ii.graphs import PlanComponent, RunPlan

from .hosts import Gate

type HostsFactory = Callable[[RunPlan], Hosts]


class FakeRunHosts:
    """`RunHosts` fake around any `engine.Hosts`; `close` is recorded in its launcher."""

    def __init__(self, run_id: str, hosts: Hosts, closed: list[str]) -> None:
        self._run_id = run_id
        self._hosts = hosts
        self._closed = closed

    async def activate(
        self, context: CallContext, message: JsonValue
    ) -> tuple[Emission, ...] | CallFailure:
        return await self._hosts.activate(context, message)

    async def select_output(
        self, context: CallContext, received: JsonValue, node_input: JsonValue
    ) -> Emission | CallFailure:
        return await self._hosts.select_output(context, received, node_input)

    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure:
        return await self._hosts.recall(context, message)

    async def remember(
        self, context: CallContext, received: JsonValue, replied: JsonValue
    ) -> None | CallFailure:
        return await self._hosts.remember(context, received, replied)

    async def close(self) -> None:
        self._closed.append(self._run_id)


class FakeHostLauncher:
    """`HostLauncher` fake. Records `host.ready` per package host; `failure` makes the last host
    fail with `host.failed` and `StartupFailed`; `gate` holds the launch until it opens."""

    def __init__(self, hosts: HostsFactory, failure: str | None = None) -> None:
        self.failure = failure
        self.gate: Gate | None = None
        self.launched: list[str] = []
        self.closed: list[str] = []
        self._hosts = hosts

    async def launch(self, run_id: str, plan: RunPlan, log: RunLog) -> FakeRunHosts:
        self.launched.append(run_id)
        if self.gate is not None:
            await self.gate.wait()
        for node in plan.nodes.values():
            parts = [("node", node.host), ("output", node.embedded_output)]
            for position, part in parts:
                if node.kind == "package" and part is not None:
                    _ready(log, node.id, position, part, self.failure)
        if self.failure is not None:
            raise StartupFailed(self.failure)
        return FakeRunHosts(run_id, self._hosts(plan), self.closed)


def _ready(
    log: RunLog, node_id: str, position: str, part: PlanComponent, failure: str | None
) -> None:
    component = str(part.declaration.ref)
    if failure is None:
        ready: JsonObject = {"position": position, "component": component, "startup_ms": 0}
        log.record("host.ready", ready, node_id=node_id)
        return
    error: JsonObject = {"code": "not_ready", "message": failure}
    failed: JsonObject = {"position": position, "component": component, "error": error}
    log.record("host.failed", failed, node_id=node_id)
