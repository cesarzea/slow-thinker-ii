"""FIFO deliveries, bounded concurrency, stateful nodes, fan-out and discarded emissions."""

from slow_thinker_ii.engine import Emission
from support.hosts import Gate, echo, emit

from .documents import fan_out, stateful_merge, unconnected
from .harness import STORY, harness


async def test_running_activations_never_exceed_the_limit() -> None:
    bounded = harness(fan_out(5, 2), {f"w{index}": echo() for index in range(1, 6)})
    outcome = await bounded.engine.run(STORY)
    assert (outcome.status, outcome.activations, outcome.messages) == ("completed", 11, 10)
    assert bounded.hosts.peak == 2
    free = harness(fan_out(5, 4), {f"w{index}": echo() for index in range(1, 6)})
    await free.engine.run(STORY)
    assert free.hosts.peak == 4


async def test_deliveries_start_in_first_in_first_out_order() -> None:
    run = harness(fan_out(3, 1), {f"w{index}": echo() for index in range(1, 4)})
    outcome = await run.engine.run(STORY)
    started = run.log.of("activation.started")
    order = [(event.node_id, event.data["message_id"]) for event in started]
    assert order == [
        ("story", None),
        ("w1", "m1"),
        ("w2", "m2"),
        ("w3", "m3"),
        ("result", "m4"),
        ("result", "m5"),
        ("result", "m6"),
    ]
    assert [result.message_id for result in outcome.results] == ["m4", "m5", "m6"]
    trigger = run.log.of("activation.completed")[0]
    assert trigger.data == {
        "emitted": [{"port": "out", "message_ids": ["m1", "m2", "m3"]}],
        "duration_ms": 0,
    }


async def test_a_busy_stateful_node_fails_the_new_activation() -> None:
    gate = Gate()
    behaviours = {"p1": echo(), "p2": echo(), "merge": emit(Emission("out", "merged"), gate=gate)}
    run = harness(stateful_merge(), behaviours)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("failed", "activation_failed")
    assert outcome.detail == (
        "Merge activation 2 failed: the node is still running an earlier activation."
    )
    failed = run.log.of("activation.failed")[0]
    assert (failed.node_id, failed.activation_id) == ("merge", "a5")
    assert failed.data["error"] == {
        "code": "node_busy",
        "message": "The node is still running an earlier activation.",
    }
    cancelled = run.log.of("activation.cancelled")
    assert [(event.activation_id, event.data) for event in cancelled] == [
        ("a4", {"reason": "activation_failed"})
    ]
    assert outcome.activations == 5


async def test_a_stateful_node_runs_again_once_free() -> None:
    behaviours = {"p1": echo(), "p2": echo(), "merge": echo()}
    run = harness(stateful_merge(max_running_nodes=1), behaviours)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.activations, len(outcome.results)) == ("completed", 7, 2)
    merges = [event for event in run.log.of("activation.started") if event.node_id == "merge"]
    assert [event.data["number"] for event in merges] == [1, 2]


async def test_an_emission_without_connections_is_discarded() -> None:
    run = harness(unconnected(), {"proposer": emit(Emission("out", "lost"))})
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.results, outcome.messages) == ("completed", (), 1)
    discarded = run.log.of("message.discarded")[0]
    assert (discarded.node_id, discarded.activation_id) == ("proposer", "a2")
    assert discarded.data == {
        "from": {"node_id": "proposer", "port": "out"},
        "reason": "no_connection",
        "payload": "lost",
    }
    completed = run.log.of("activation.completed")[1]
    assert completed.data["emitted"] == [{"port": "out", "message_ids": []}]


async def test_several_emissions_keep_their_order() -> None:
    emissions = (Emission("out", "one"), Emission("out", "two"))
    run = harness(fan_out(1, 4), {"w1": emit(*emissions)})
    outcome = await run.engine.run(STORY)
    assert [result.payload for result in outcome.results] == ["one", "two"]
    completed = run.log.of("activation.completed")[1]
    assert completed.data["emitted"] == [
        {"port": "out", "message_ids": ["m2"]},
        {"port": "out", "message_ids": ["m3"]},
    ]
