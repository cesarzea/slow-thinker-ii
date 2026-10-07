"""Runs of a change: what is on screen runs without being activated, traced to its change."""

import pytest
from slow_thinker_ii.application import ChangeNotFound, GraphNotFound
from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Hosts
from slow_thinker_ii.graphs import RunPlan
from support.examples import (
    J1,
    graph_document,
    memory_declaration,
    step_one_catalog,
    with_memory,
)
from support.hosts import ScriptedHosts, echo
from support.platform import Platform

STORY = "A cat tried to learn to fly."


async def test_a_change_runs_without_being_activated() -> None:
    platform = Platform()
    graph_id = platform.saved(J1)
    renamed = {**graph_document(J1), "name": "Funnier story"}
    change, _, _ = platform.library.record_change(graph_id, "main", renamed)
    run_id = await platform.runs.start(graph_id, None, change=change)
    record = await platform.finish(run_id)
    assert (record.version, record.change, record.status) == (None, 2, "completed")
    assert record.to_json()["version"] is None and record.to_json()["change"] == 2
    started = platform.run_store.of(run_id, "run.started")[0]
    assert (started.data["graph_version"], started.data["graph_change"]) == (None, 2)
    activated = await platform.finish(await platform.runs.start(graph_id, None, change=1))
    assert (activated.version, activated.change) == (1, 1)


async def test_a_run_needs_a_known_graph_and_change() -> None:
    platform = Platform()
    graph_id = platform.saved(J1)
    with pytest.raises(ChangeNotFound):
        await platform.runs.start(graph_id, None, change=9)
    with pytest.raises(GraphNotFound):
        await platform.runs.start("missing", None, change=1)
    with pytest.raises(ValueError, match="version or a change"):
        await platform.runs.start(graph_id, None)


class MemoryCallers(ScriptedHosts):
    """Records which component each memory call's grant names, as the gateway would see it."""

    def __init__(self, platform: Platform) -> None:
        super().__init__({"proposer": echo()})
        self.platform = platform
        self.components: list[str] = []

    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure:
        call = self.platform.runs.active_call(context.grant)
        assert call is not None
        self.components.append(str(call.component.declaration.ref))
        return await super().recall(context, message)


async def test_a_memory_call_acts_for_the_memory_component() -> None:
    hosts: list[MemoryCallers] = []

    def factory(_plan: RunPlan) -> Hosts:
        hosts.append(MemoryCallers(platform))
        return hosts[-1]

    platform = Platform(hosts=factory)
    platform.catalog = step_one_catalog(memory_declaration())
    graph_id = platform.saved(with_memory(graph_document(J1), "proposer"))
    record = await platform.finish(await platform.runs.start(graph_id, 1))
    assert record.status == "completed"
    assert hosts[0].components == ["memory@1.0.0"]
    assert hosts[0].remembered == [("proposer", STORY, {"remembered": [], "message": STORY})]
