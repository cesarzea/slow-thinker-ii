"""Run listings with live status, event pages, run views, recovery and shutdown."""

import pytest
from slow_thinker_ii.accounting import Scope
from slow_thinker_ii.application import NewEvent, RunNotFound, RunRecord
from slow_thinker_ii.contracts import JsonObject
from support.examples import FLASH, J1, J2, J3
from support.platform import Platform
from support.providers import reply

from .held import held_call, stopped


async def test_runs_are_listed_newest_first_with_their_live_status() -> None:
    platform = Platform(steps={FLASH: [reply('{"score": 8}')]})
    first = await platform.completed(J1)
    context = await held_call(platform, J2)
    listed = platform.runs.runs(None, 10)
    assert [(run.run_id, run.status) for run in listed] == [
        (context.run_id, "running"),
        (first.run_id, "completed"),
    ]
    assert [run.run_id for run in platform.runs.runs("funny-story", 0)] == [first.run_id]
    assert platform.runs.run(context.run_id).summary.status == "running"
    page = platform.runs.events(context.run_id, 0, 500)
    assert not page.finished
    await stopped(platform, context)


async def test_events_are_paged_until_the_end_of_a_finished_run() -> None:
    platform = Platform()
    record = await platform.completed(J1)
    count = len(platform.run_store.kinds(record.run_id))
    first = platform.runs.events(record.run_id, 0, 5)
    assert ([event.seq for event in first.events], first.last_seq, first.finished) == (
        [1, 2, 3, 4, 5],
        5,
        False,
    )
    rest = platform.runs.events(record.run_id, 5, 500)
    assert (rest.last_seq, rest.finished, rest.events[-1].kind) == (count, True, "run.finished")
    assert platform.runs.events(record.run_id, 0, count).finished
    empty = platform.runs.events(record.run_id, count, 10)
    assert (empty.events, empty.last_seq, empty.finished) == ((), count, True)
    assert len(platform.runs.events(record.run_id, 0, 0).events) == 1
    with pytest.raises(RunNotFound):
        platform.runs.events("missing", 0, 10)


async def test_the_run_view_counts_activations_and_messages() -> None:
    platform = Platform(steps={FLASH: [reply('{"score": 5}'), reply('{"score": 8}')]})
    record = await platform.completed(J3)
    view = platform.runs.run(record.run_id)
    assert dict(view.activations_by_node) == {"story": 1, "proposer": 2, "reviewer": 2, "result": 1}
    assert dict(view.messages_by_connection) == {
        "story.out -> proposer.in": 1,
        "proposer.out -> reviewer.in": 2,
        "reviewer.revise -> proposer.in": 1,
        "reviewer.accepted -> result.in": 1,
    }
    assert [result["node_id"] for result in view.results] == ["result"]
    with pytest.raises(RunNotFound):
        platform.runs.run("missing")


async def test_long_logs_are_read_in_pages() -> None:
    platform = Platform()
    _unfinished(platform, "long")
    for _ in range(600):
        _event(platform, "long", "report", {"kind": "step", "content": "Working."})
    assert platform.runs.run("long").activations_by_node == {}
    assert len(platform.runs.events("long", 0, 1000).events) == 500


async def test_recovery_marks_unfinished_runs_interrupted() -> None:
    platform = Platform()
    _unfinished(platform, "crashed")
    usage: JsonObject = {"input": 10, "cached_input": 2, "cache_write": 0, "output": 5}
    events: list[tuple[str, JsonObject]] = [
        ("activation.started", {"message_id": None, "number": 1}),
        ("message.sent", {"message_id": "m1"}),
        ("llm.called", {"usage": usage, "cost_usd": "0.000010000"}),
        ("message.dropped", {"message_id": "m1"}),
    ]
    for kind, data in events:
        _event(platform, "crashed", kind, data)
    scopes = [Scope("run", "crashed", 10**8, 0), Scope("day", "2026-10-05", 10**9, 0)]
    scopes.append(Scope("month", "2026-10", 5 * 10**9, 0))
    platform.ledger.reserve("open-call", "crashed", scopes, 1_000, platform.clock.now())
    platform.clock.advance(2)
    platform.runs.recover()
    record = platform.run_store.run("crashed")
    assert record is not None
    assert (record.status, record.reason) == ("failed", "interrupted")
    assert record.detail == "The backend restarted before the run finished."
    totals = {"duration_ms": 2000, "activations": 1, "messages": 1, "llm_calls": 1}
    totals |= {"input_tokens": 12, "output_tokens": 5, "cost_usd": "0.000010000"}
    assert record.totals == totals
    finished = platform.run_store.of("crashed", "run.finished")[0]
    assert (finished.elapsed_ms, finished.data["dropped"]) == (2000, 1)
    row = platform.ledger.rows["open-call"]
    assert (row.charge, row.estimated) == (1_000, True)
    assert platform.run_store.unfinished() == ()


async def test_shutdown_cancels_active_runs_and_waits_for_them() -> None:
    platform = Platform()
    context = await held_call(platform)
    await platform.runs.shutdown()
    record = platform.run_store.run(context.run_id)
    assert record is not None and record.status == "cancelled"
    assert record.detail == "The platform shut down before the run finished."
    assert platform.launcher.closed == [context.run_id]
    await platform.runs.shutdown()


def _unfinished(platform: Platform, run_id: str) -> None:
    now = platform.clock.now()
    record = RunRecord(run_id, "funny-story", 1, 1, "running", None, "", "x", now, None, None)
    platform.run_store.create(record)


def _event(platform: Platform, run_id: str, kind: str, data: JsonObject) -> None:
    event = NewEvent(platform.clock.now(), 0, kind, "observed", "story", None, data)
    platform.run_store.append(run_id, event)
