"""Run summaries: creation, terminal status, listings and restart candidates."""

import sqlite3
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteRunStore
from slow_thinker_ii.application import RunNotFound, RunRecord
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .stores import AT, initialized, later, starting, with_graph

TOTALS: JsonObject = {"duration_ms": 1200, "llm_calls": 1, "cost_usd": "0.000001000"}
MESSAGES: list[JsonValue] = [None, "A cat tried to learn to fly.", {"b": [1, 2.5], "a": True}]


@pytest.mark.parametrize("message", MESSAGES)
def test_a_created_run_reads_back_unchanged(tmp_path: Path, message: JsonValue) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    record = starting("r1", input=message)
    store.create(record)
    assert store.run("r1") == record
    assert store.run("missing") is None


def test_a_run_finishes_once_with_its_status_and_totals(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    store.create(starting("r1"))
    store.finish("r1", "stopped", "max_activations", "The limit was reached.", TOTALS, later(2))
    assert store.run("r1") == RunRecord(
        "r1",
        "funny-story",
        1,
        1,
        "stopped",
        "max_activations",
        "The limit was reached.",
        "Hi",
        AT,
        later(2),
        TOTALS,
    )
    with pytest.raises(ValueError, match="already finished"):
        store.finish("r1", "failed", "interrupted", "Again.", TOTALS, later(3))
    with pytest.raises(RunNotFound):
        store.finish("missing", "failed", "interrupted", "Unknown.", TOTALS, later(3))
    finished = store.run("r1")
    assert finished is not None and finished.status == "stopped"


def test_runs_are_listed_newest_first_per_graph(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(with_graph(initialized(tmp_path)), "story-triage"))
    store.create(starting("old", at=later(-10)))
    store.create(starting("tied-1"))
    store.create(starting("tied-2"))
    store.create(starting("triage", "story-triage", later(5)))
    assert [run.run_id for run in store.runs(None, 10)] == ["triage", "tied-2", "tied-1", "old"]
    assert [run.run_id for run in store.runs("funny-story", 2)] == ["tied-2", "tied-1"]
    assert store.runs("story-triage", 0) == () and store.runs(None, -1) == ()
    assert store.runs("missing", 10) == ()


def test_unfinished_runs_are_those_without_a_terminal_status(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    for run_id, at in (("second", later(1)), ("first", AT), ("done", later(2))):
        store.create(starting(run_id, at=at))
    store.finish("done", "completed", None, "", TOTALS, later(3))
    assert store.unfinished() == ("first", "second")


def test_a_run_of_a_change_never_activated_has_no_version(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    store.create(
        RunRecord("r1", "funny-story", None, 1, "starting", None, "", None, AT, None, None)
    )
    run = store.run("r1")
    assert run is not None and (run.version, run.change) == (None, 1)


def test_runs_refer_to_stored_graph_versions(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    with pytest.raises(sqlite3.IntegrityError):
        store.create(
            RunRecord("r1", "funny-story", 2, 2, "starting", None, "", None, AT, None, None)
        )
    with pytest.raises(sqlite3.IntegrityError):
        store.create(
            RunRecord("r1", "funny-story", None, 5, "starting", None, "", None, AT, None, None)
        )
    with pytest.raises(sqlite3.IntegrityError):
        store.create(starting("r2", "missing"))
    assert store.runs(None, 10) == ()
