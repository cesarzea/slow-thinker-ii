"""The validated journeys J1–J3 run on plans compiled from the contract examples."""

from slow_thinker_ii.engine import RunResult
from support.examples import J1, J2, J3, journey_plan
from support.hosts import scores
from support.selections import route_by_score

from .harness import STORY, harness, review, rewrite

J1_EVENTS = [
    "run.running",
    "activation.started",
    "message.sent",
    "activation.completed",
    "activation.started",
    "component.called",
    "message.sent",
    "activation.completed",
    "activation.started",
    "run.result",
    "activation.completed",
]


async def test_one_agent_completes_with_its_result() -> None:
    run = harness(journey_plan(J1), {"proposer": rewrite})
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason, outcome.detail) == ("completed", None, "")
    payload = f"Funny: {STORY}"
    assert outcome.results == (RunResult("result", "Funny story", "m2", payload),)
    assert (outcome.activations, outcome.messages) == (3, 2)
    result = run.log.of("run.result")[0]
    assert result.data == {"name": "Funny story", "message_id": "m2", "payload": payload}
    assert (result.node_id, result.activation_id) == ("result", "a3")


async def test_events_follow_the_run_in_order_with_identifiers() -> None:
    run = harness(journey_plan(J1), {"proposer": rewrite})
    await run.engine.run(STORY)
    assert run.log.kinds() == J1_EVENTS
    started = run.log.of("activation.started")
    assert [(event.node_id, event.activation_id) for event in started] == [
        ("story", "a1"),
        ("proposer", "a2"),
        ("result", "a3"),
    ]
    assert [event.data for event in started] == [
        {"message_id": None, "number": 1},
        {"message_id": "m1", "number": 1},
        {"message_id": "m2", "number": 1},
    ]
    sent = run.log.of("message.sent")
    assert [(event.node_id, event.activation_id) for event in sent] == [
        ("story", "a1"),
        ("proposer", "a2"),
    ]
    assert sent[1].data == {
        "message_id": "m2",
        "from": {"node_id": "proposer", "port": "out"},
        "to": {"node_id": "result", "port": "in"},
        "payload": f"Funny: {STORY}",
    }
    [issued] = run.grants.issued
    assert (issued.ttl_seconds, run.hosts.calls[0].budget_ms) == (300.0, 300_000)


async def test_an_embedded_router_selects_one_output() -> None:
    plan = journey_plan(J2)
    select = {"judge": route_by_score("funny", "not_funny")}
    funny = harness(plan, {"judge": scores(8)}, select)
    outcome = await funny.engine.run(STORY)
    assert outcome.results == (RunResult("funny", "Funny", "m2", STORY),)
    plain = harness(plan, {"judge": scores(3)}, select)
    outcome = await plain.engine.run(STORY)
    assert outcome.results == (RunResult("not-funny", "Not funny", "m2", STORY),)
    calls = plain.log.of("component.called")
    assert [event.data["operation"] for event in calls] == ["activate", "select_output"]
    assert calls[1].data == {
        "position": "output",
        "component": "router@1.0.0",
        "operation": "select_output",
        "arguments": {"received": {"score": 3}, "node_input": STORY},
        "result": {"port": "not_funny", "payload": STORY},
        "duration_ms": 0,
    }
    sent = plain.log.of("message.sent")[1]
    assert sent.data["from"] == {"node_id": "judge", "port": "not_funny"}


async def test_the_review_loop_completes_when_the_reviewer_accepts() -> None:
    activate, select = review(5, 8)
    run = harness(journey_plan(J3), activate, select)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.activations, outcome.messages) == ("completed", 6, 5)
    revised = f"Funny: Funny: {STORY}"
    assert outcome.results == (RunResult("result", "Funny story", "m5", revised),)
    started = run.log.of("activation.started")
    numbers = [(event.node_id, event.data["number"]) for event in started]
    assert numbers == [
        ("story", 1),
        ("proposer", 1),
        ("reviewer", 1),
        ("proposer", 2),
        ("reviewer", 2),
        ("result", 1),
    ]


async def test_the_review_loop_stops_at_the_activation_limit() -> None:
    activate, select = review(6)
    run = harness(journey_plan(J3), activate, select)
    outcome = await run.engine.run(STORY)
    assert (outcome.status, outcome.reason) == ("stopped", "activation_limit")
    assert (
        outcome.detail == "The run reached its limit of 10 activations before Reviewer could start."
    )
    assert (outcome.activations, outcome.messages, outcome.results) == (10, 10, ())
    nodes = [event.node_id for event in run.log.of("activation.started")]
    assert (nodes.count("story"), nodes.count("proposer"), nodes.count("reviewer")) == (1, 5, 4)
    dropped = run.log.of("message.dropped")
    assert [(event.node_id, event.activation_id, event.data) for event in dropped] == [
        (
            "reviewer",
            None,
            {
                "message_id": "m10",
                "to": {"node_id": "reviewer", "port": "in"},
                "reason": "run_ending",
            },
        )
    ]
    assert run.log.kinds()[-1] == "message.dropped"
    assert not run.log.of("activation.cancelled")
