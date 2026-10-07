"""An engine wired to the shared fakes, with the journeys' scripted component behaviours."""

from collections.abc import Mapping
from dataclasses import dataclass

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, Emission, RunEngine
from slow_thinker_ii.graphs import RunPlan
from support.clock import FakeClock
from support.grants import RecordingGrants
from support.hosts import Activate, Recall, ScriptedHosts, Select, scores
from support.log import RecordingLog
from support.selections import route_by_score

STORY = "A cat tried to learn to fly."


@dataclass(frozen=True)
class Harness:
    clock: FakeClock
    log: RecordingLog
    grants: RecordingGrants
    hosts: ScriptedHosts
    engine: RunEngine


def harness(
    plan: RunPlan,
    activate: Mapping[str, Activate],
    select: Mapping[str, Select] | None = None,
    *,
    recall: Mapping[str, Recall] | None = None,
    max_activation_seconds: int = 300,
    clock: FakeClock | None = None,
) -> Harness:
    clock = clock or FakeClock()
    log = RecordingLog()
    grants = RecordingGrants(clock)
    hosts = ScriptedHosts(activate, select, recall)
    engine = RunEngine(
        "run-1", plan, hosts, log, grants, clock, max_activation_seconds=max_activation_seconds
    )
    return Harness(clock, log, grants, hosts, engine)


async def rewrite(_context: CallContext, message: JsonValue) -> tuple[Emission, ...]:
    """The Proposer's LLM Call: a funnier version of the received story."""
    return (Emission("out", f"Funny: {message}"),)


def review(*values: int) -> tuple[dict[str, Activate], dict[str, Select]]:
    """J3 behaviours: the Reviewer scores each story; its Router accepts from 7."""
    activate: dict[str, Activate] = {"proposer": rewrite, "reviewer": scores(*values)}
    return activate, {"reviewer": route_by_score("accepted", "revise")}
