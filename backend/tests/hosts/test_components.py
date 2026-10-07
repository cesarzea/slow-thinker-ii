"""The real LLM Call and Router packages as hosts, alone and under the run engine."""

import time
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.hosts import LocalHostLauncher
from slow_thinker_ii.application import StartupFailed
from slow_thinker_ii.engine import Emission, RunEngine
from support.clock import FakeClock
from support.examples import (
    J2,
    changed,
    graph_document,
    journey_plan,
    memory_declaration,
    step_one_catalog,
    with_memory,
)
from support.grants import RecordingGrants
from support.log import RecordingLog

from .chat_endpoint import chat_endpoint
from .plans import fixture_plan
from .process_fixture import (
    PROTOCOL_FIXTURE,
    RUN,
    Targets,
    context,
    launched,
    launcher,
    settings,
)

STORY = "A cat tried to learn to fly."


async def test_llm_call_and_router_hosts_serve_the_triage_node(tmp_path: Path) -> None:
    log, targets = RecordingLog(), Targets(launcher(tmp_path))
    async with chat_endpoint('{"score": 8}') as endpoint:
        host_settings = settings(tmp_path, llm_base_url=endpoint.base_url)
        async with launched(journey_plan(J2), host_settings, targets, log) as hosts:
            emitted = await hosts.activate(context("judge"), STORY)
            chosen = await hosts.select_output(context("judge", "output"), {"score": 8}, STORY)
    assert emitted == (Emission("out", {"score": 8}),)
    assert chosen == Emission("funny", STORY)
    ((request, authorization),) = endpoint.requests
    assert authorization == "Bearer grant-judge-node"
    assert request["model"] == "deepseek/deepseek-flash"
    assert request["messages"] == [
        {"role": "system", "content": "Rate how funny this story is from 1 to 10."},
        {"role": "user", "content": STORY},
    ]
    ready = sorted(
        (event.data["position"], event.data["component"]) for event in log.of("host.ready")
    )
    assert ready == [("node", "llm-call@1.0.0"), ("output", "router@1.0.0")]


async def test_the_engine_runs_story_triage_on_real_hosts(tmp_path: Path) -> None:
    clock, log, plan = FakeClock(), RecordingLog(), journey_plan(J2)
    grants = RecordingGrants(clock)
    async with chat_endpoint('{"score": 9}') as endpoint:
        host_settings = settings(tmp_path, llm_base_url=endpoint.base_url)
        async with launched(plan, host_settings, Targets(launcher(tmp_path)), log) as hosts:
            outcome = await RunEngine(RUN, plan, hosts, log, grants, clock).run(STORY)
    assert (outcome.status, outcome.reason) == ("completed", None)
    assert [(result.name, result.payload) for result in outcome.results] == [("Funny", STORY)]
    judge = [issued.token for issued in grants.issued if issued.caller.node_id == "judge"]
    assert [authorization for _, authorization in endpoint.requests] == [f"Bearer {judge[0]}"]


async def test_a_router_script_that_does_not_compile_fails_the_start(tmp_path: Path) -> None:
    script = "def route(received, node_input)\n    return 'funny', received\n"
    document = changed(graph_document(J2), ("nodes", 1, "embedded", 0, "config", "script"), script)
    log = RecordingLog()
    launch = LocalHostLauncher(Targets(launcher(tmp_path)), settings(tmp_path))
    with pytest.raises(StartupFailed) as failed:
        await launch.launch(RUN, journey_plan(document), log)
    assert str(failed.value) == (
        "Router in Judge could not start: Router startup failed: "
        "The script has a syntax error at line 1: expected ':'"
    )
    assert [event.kind for event in log.events if event.data["position"] == "output"] == [
        "host.failed"
    ]


class RealClock:
    def monotonic(self) -> float:
        return time.monotonic()


async def test_the_run_deadline_decides_when_a_host_never_answers(tmp_path: Path) -> None:
    plan, log = fixture_plan("silent_call", time_limit_seconds=1), RecordingLog()
    targets = Targets(launcher(tmp_path, PROTOCOL_FIXTURE))
    async with launched(plan, settings(tmp_path), targets, log) as hosts:
        engine = RunEngine(RUN, plan, hosts, log, RecordingGrants(FakeClock()), RealClock())
        outcome = await engine.run("A cat.")
    assert (outcome.status, outcome.reason) == ("stopped", "time_limit")
    assert outcome.detail == "The run reached its time limit of 1 seconds."


async def test_a_memory_host_serves_its_node_beside_the_llm_call_and_router(tmp_path: Path) -> None:
    log, targets = RecordingLog(), Targets(launcher(tmp_path))
    document = with_memory(graph_document(J2), "judge", max_exchanges=1)
    plan = journey_plan(document, step_one_catalog(memory_declaration()))
    async with launched(plan, settings(tmp_path), targets, log) as hosts:
        memory = context("judge", "memory")
        first = await hosts.recall(memory, STORY)
        kept = await hosts.remember(memory, STORY, {"score": 8})
        second = await hosts.recall(memory, "Another story.")
    assert first == STORY and kept is None
    assert second == (
        f'Conversation so far:\nYou received: {STORY}\nYou replied: {{"score":8}}\n\n'
        "New message:\nAnother story."
    )
    ready = sorted(
        (event.data["position"], event.data["component"]) for event in log.of("host.ready")
    )
    assert ready == [
        ("memory", "memory@1.0.0"),
        ("node", "llm-call@1.0.0"),
        ("output", "router@1.0.0"),
    ]


async def test_memory_calls_without_a_memory_host_fail(tmp_path: Path) -> None:
    log, targets = RecordingLog(), Targets(launcher(tmp_path))
    async with launched(journey_plan(J2), settings(tmp_path), targets, log) as hosts:
        recalled = await hosts.recall(context("judge", "memory"), STORY)
        kept = await hosts.remember(context("judge", "memory"), STORY, "Reply")
    missing = 'No component host serves the node "judge".'
    assert [getattr(item, "message", None) for item in (recalled, kept)] == [missing, missing]
