"""A node's memory: the platform calls its `recall` before the host and its `remember` after."""

from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission
from slow_thinker_ii.graphs import RunPlan
from support.examples import (
    J1,
    J3,
    graph_document,
    journey_plan,
    memory_declaration,
    step_one_catalog,
    with_memory,
)
from support.hosts import Activate

from .harness import STORY, harness, review


def remembered_plan(name: str, node: str) -> RunPlan:
    document = with_memory(graph_document(name), node)
    return journey_plan(document, step_one_catalog(memory_declaration()))


def received(log: list[JsonValue]) -> Activate:
    async def behaviour(_context: CallContext, message: JsonValue) -> tuple[Emission, ...]:
        log.append(message)
        return (Emission("out", f"Reply {len(log)}"),)

    return behaviour


async def test_the_node_receives_what_its_memory_recalls_and_its_replies_are_remembered() -> None:
    plan = remembered_plan(J1, "proposer")
    assert plan.node("proposer").embedded_memory is not None
    assert plan.node("proposer").stateful
    messages: list[JsonValue] = []
    run = harness(plan, {"proposer": received(messages)})
    outcome = await run.engine.run(STORY)
    assert outcome.status == "completed"
    assert messages == [{"remembered": [], "message": STORY}]
    assert run.hosts.remembered == [("proposer", STORY, "Reply 1")]
    calls = [
        (event.data["position"], event.data["operation"])
        for event in run.log.of("component.called")
    ]
    assert calls == [("memory", "recall"), ("node", "activate"), ("memory", "remember")]
    recall, _, remember = run.log.of("component.called")
    assert recall.data["component"] == "memory@1.0.0"
    assert recall.data["arguments"] == {"message": STORY}
    assert recall.data["result"] == {"message": {"remembered": [], "message": STORY}}
    assert remember.data["arguments"] == {"received": STORY, "replied": "Reply 1"}
    assert remember.data["result"] == {}
    positions = [context.position for context in run.hosts.calls]
    assert positions == ["memory", "node", "memory"]


async def test_the_memory_keeps_the_reply_before_the_router_chooses_its_output() -> None:
    activate, select = review(5, 8)
    plan = remembered_plan(J3, "reviewer")
    run = harness(plan, activate, select)
    outcome = await run.engine.run(STORY)
    assert outcome.status == "completed"
    assert [replied for _, _, replied in run.hosts.remembered] == [{"score": 5}, {"score": 8}]
    operations = [event.data["operation"] for event in run.log.of("component.called")]
    reviewer = [op for op in operations if op in ("recall", "remember", "select_output")]
    assert reviewer == ["recall", "remember", "select_output"] * 2


async def test_a_memory_that_fails_fails_the_activation() -> None:
    async def broken(_context: CallContext, _message: JsonValue) -> CallFailure:
        return CallFailure("memory_error", "The memory is unavailable.")

    plan = remembered_plan(J1, "proposer")
    run = harness(plan, {"proposer": received([])}, recall={"proposer": broken})
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "activation_failed")
    assert outcome.detail == "Proposer activation 1 failed: the memory is unavailable."
    assert [context.position for context in run.hosts.calls] == ["memory"]
    forgetful = harness(plan, {"proposer": received([])})
    forgetful.hosts.forget = CallFailure("memory_error", "Nothing can be kept.")
    outcome = await forgetful.engine.run(STORY)
    assert outcome.detail == "Proposer activation 1 failed: nothing can be kept."
