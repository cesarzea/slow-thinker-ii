"""Event logs: gap-free sequence numbers, pages and concurrent appends."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteRunStore
from slow_thinker_ii.application import NewEvent, RecordedEvent
from slow_thinker_ii.contracts import JsonObject

from .stores import AT, initialized, observed, starting, with_graph

SENT: JsonObject = {
    "message_id": "m1",
    "from": {"node_id": "story", "port": "out"},
    "to": {"node_id": "proposer", "port": "in"},
    "payload": "A cat tried to learn to fly.",
}


def test_appended_events_are_numbered_and_read_back_as_recorded(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    store.create(starting("r1"))
    store.create(starting("r2"))
    first = store.append("r1", observed("run.started", {"graph_id": "funny-story"}))
    sent = NewEvent(AT, 12, "message.sent", "observed", "story", "a1", SENT)
    second = store.append("r1", sent)
    other = store.append("r2", observed())
    assert second == RecordedEvent("r1", 2, AT, 12, "message.sent", "observed", "story", "a1", SENT)
    assert (first.seq, other.seq) == (1, 1)
    assert store.events("r1", 0, 10) == (first, second)
    assert store.events("r2", 0, 10) == (other,)


def test_event_pages_start_after_a_sequence_number(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    store.create(starting("r1"))
    appended = [store.append("r1", observed("activation.started", {"number": n})) for n in range(5)]
    assert store.events("r1", 0, 2) == tuple(appended[:2])
    assert store.events("r1", 2, 2) == tuple(appended[2:4])
    assert store.events("r1", 4, 10) == (appended[4],)
    assert store.events("r1", 5, 10) == ()
    assert store.events("r1", 0, 0) == () and store.events("r1", 0, -1) == ()
    assert store.events("missing", 0, 10) == ()


def test_concurrent_appends_get_distinct_consecutive_numbers(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    store.create(starting("r1"))

    def append(index: int) -> int:
        return store.append("r1", observed("report", {"index": index})).seq

    with ThreadPoolExecutor(max_workers=8) as pool:
        numbers = list(pool.map(append, range(64)))
    assert sorted(numbers) == list(range(1, 65))
    stored = store.events("r1", 0, 100)
    assert [event.seq for event in stored] == list(range(1, 65))
    indices = [event.data["index"] for event in stored]
    assert sorted(index for index in indices if isinstance(index, int)) == list(range(64))


def test_events_need_an_existing_run_and_a_known_evidence(tmp_path: Path) -> None:
    store = SqliteRunStore(with_graph(initialized(tmp_path)))
    with pytest.raises(sqlite3.IntegrityError):
        store.append("missing", observed())
    store.create(starting("r1"))
    with pytest.raises(sqlite3.IntegrityError):
        store.append("r1", NewEvent(AT, 0, "report", "guessed", None, None, {}))
    assert store.events("r1", 0, 10) == ()
