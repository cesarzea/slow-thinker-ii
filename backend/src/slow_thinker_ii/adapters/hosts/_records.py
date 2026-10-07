"""The run's record of each host, `host.ready` or `host.failed`, and the hosts of a plan."""

from collections.abc import Mapping

from slow_thinker_ii.application import StartupFailed
from slow_thinker_ii.catalog import ComponentRef
from slow_thinker_ii.contracts import JsonObject
from slow_thinker_ii.engine import Position, RunLog
from slow_thinker_ii.graphs import PlanComponent, PlanNode, RunPlan

from ._readiness import NotReady
from ._resolution import Target

type Part = tuple[PlanNode, Position, PlanComponent]


def plan_parts(plan: RunPlan) -> list[Part]:
    parts: list[Part] = []
    for node in plan.nodes.values():
        if node.kind == "package":
            parts.append((node, "node", node.host))
            if node.embedded_output is not None:
                parts.append((node, "output", node.embedded_output))
            if node.embedded_memory is not None:
                parts.append((node, "memory", node.embedded_memory))
    return parts


def not_installed(
    parts: list[Part], found: Mapping[ComponentRef, Target | NotReady], log: RunLog
) -> StartupFailed:
    """Every host of an uninstalled component fails; the others are never started."""
    details: list[str] = []
    for part in parts:
        result = found[component_of(part)]
        if isinstance(result, NotReady):
            details.append(f"{host_name(part)} could not start: {result.cause}")
            record_failure(log, part, result.code, details[-1])
        else:
            record_failure(
                log, part, "stopped", f"{host_name(part)} was stopped before it was ready."
            )
    return StartupFailed(details[0])


def component_of(part: Part) -> ComponentRef:
    return part[2].declaration.ref


def host_name(part: Part) -> str:
    return f"{part[2].declaration.label} in {part[0].name}"


def component_name(part: Part) -> str:
    return str(component_of(part))


def record_failure(log: RunLog, part: Part, code: str, message: str) -> None:
    error: JsonObject = {"code": code, "message": message}
    failed: JsonObject = {"position": part[1], "component": component_name(part), "error": error}
    log.record("host.failed", failed, node_id=part[0].id)


def record_ready(log: RunLog, part: Part, startup_ms: int) -> None:
    ready: JsonObject = {
        "position": part[1],
        "component": component_name(part),
        "startup_ms": startup_ms,
    }
    log.record("host.ready", ready, node_id=part[0].id)
