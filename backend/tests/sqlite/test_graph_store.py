"""The working copy of branch `main`: numbered changes, dedupe, paging and activated versions."""

from datetime import datetime
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteGraphStore
from slow_thinker_ii.application import (
    BranchNotFound,
    BranchSummary,
    ChangeNotFound,
    ChangeRecord,
    ChangeSummary,
    GraphExists,
    GraphNotFound,
    GraphRecord,
    GraphSummary,
    VersionRecord,
    VersionSummary,
)
from slow_thinker_ii.contracts import JsonObject
from support.examples import J1, graph_document

from .stores import AT, initialized, later

MAIN = BranchSummary("main", AT, None, None, 1, None)


def named(name: str) -> JsonObject:
    document = graph_document(J1)
    document["name"] = name
    return document


def test_a_new_graph_is_branch_main_with_change_1_and_no_version(tmp_path: Path) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    store.create("funny-story", "Funny story", named("Funny story"), AT)
    first = ChangeRecord("funny-story", 1, "main", AT, named("Funny story"), None)
    assert store.latest_change("funny-story", "main") == first == store.change("funny-story", 1)
    assert store.branches("funny-story") == (MAIN,)
    record = GraphRecord("funny-story", "Funny story", None, 1, (MAIN,), ())
    assert store.graph("funny-story") == record
    assert store.graphs() == (GraphSummary("funny-story", "Funny story", None, 1, AT),)
    with pytest.raises(GraphExists):
        store.create("funny-story", "Other", named("Other"), later(1))
    assert store.graph("missing") is None and store.branches("missing") == ()


def test_changes_are_numbered_and_unknown_targets_are_refused(tmp_path: Path) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    store.create("funny-story", "Funny story", named("Funny story"), AT)
    assert store.add_change("funny-story", "main", "Funnier", named("Funnier"), later(1)) == 2
    assert store.change("funny-story", 2) == ChangeRecord(
        "funny-story", 2, "main", later(1), named("Funnier"), None
    )
    assert store.graphs() == (GraphSummary("funny-story", "Funnier", None, 2, later(1)),)
    with pytest.raises(GraphNotFound):
        store.add_change("missing", "main", "Missing", named("Missing"), later(2))
    with pytest.raises(BranchNotFound):
        store.add_change("funny-story", "Main", "Other", named("Other"), later(2))
    assert store.change("funny-story", 3) is None
    assert store.latest_change("funny-story", "other") is None


def test_only_a_document_identical_to_the_latest_change_adds_nothing(tmp_path: Path) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    store.create("g", "Funny story", named("Funny story"), AT)
    assert store.add_change("g", "main", "Funny story", named("Funny story"), later(1)) == 1
    reordered: JsonObject = dict(reversed(list(named("Funny story").items())))
    assert store.add_change("g", "main", "Funny story", reordered, later(2)) == 2  # order counts
    assert store.add_change("g", "main", "Funny story", reordered, later(3)) == 2
    assert store.add_change("g", "main", "Funny story", named("Funny story"), later(4)) == 3
    stored = store.change("g", 2)
    assert stored is not None and list(stored.document) == list(reordered)


def test_changes_are_paged_newest_first(tmp_path: Path) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    store.create("g", "Name 1", named("Name 1"), AT)
    for number in range(2, 8):
        store.add_change("g", "main", f"Name {number}", named(f"Name {number}"), later(number))
    store.add_version("g", 3, None, later(10))
    page = store.changes("g", "main", None, 3)
    assert page == (
        ChangeSummary(7, "main", later(7), "Name 7", None),
        ChangeSummary(6, "main", later(6), "Name 6", None),
        ChangeSummary(5, "main", later(5), "Name 5", None),
    )
    following = store.changes("g", None, page[-1].change, 3)
    assert [(item.change, item.version) for item in following] == [(4, None), (3, 1), (2, None)]
    assert [item.change for item in store.changes("g", "main", 2, 3)] == [1]
    assert store.changes("g", None, 1, 3) == () and store.changes("g", "main", None, 0) == ()
    assert store.changes("missing", None, None, 3) == ()


def test_versions_are_activated_from_changes_and_follow_a_parent(tmp_path: Path) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    store.create("g", "Funny story", named("Funny story"), AT)
    store.add_change("g", "main", "Funnier", named("Funnier"), later(1))
    assert store.add_version("g", 2, None, later(2)) == 1
    assert store.add_version("g", 1, 1, later(3)) == 2
    assert store.add_version("g", 2, 2, later(4)) == 3  # again: the next version
    assert store.version("g", 2) == VersionRecord(
        "g", 2, "main", 1, 1, later(3), named("Funny story")
    )
    record = store.graph("g")
    assert record is not None and record.versions == (
        VersionSummary(1, "main", None, 2, "Funnier", later(2)),
        VersionSummary(2, "main", 1, 1, "Funny story", later(3)),
        VersionSummary(3, "main", 2, 2, "Funnier", later(4)),
    )
    assert (record.active_version, record.branches[0].head_version) == (3, 3)
    with pytest.raises(ChangeNotFound):
        store.add_version("g", 9, 3, later(5))
    assert store.version("g", 4) is None and store.version("missing", 1) is None


def test_graphs_are_listed_by_their_latest_change_and_times_must_be_aware(
    tmp_path: Path,
) -> None:
    store = SqliteGraphStore(initialized(tmp_path))
    for graph_id in ("first", "second", "third"):
        store.create(graph_id, graph_id.title(), named(graph_id.title()), AT)
    store.add_change("first", "main", "First again", named("First again"), later(5))
    store.add_version("third", 1, None, later(9))  # an activation is not a change
    listed = [(item.id, item.name, item.latest_change) for item in store.graphs()]
    assert listed == [("first", "First again", 2), ("third", "Third", 1), ("second", "Second", 1)]
    with pytest.raises(ValueError, match="timezone-aware"):
        store.add_change("first", "main", "Naive", named("Naive"), datetime(2026, 10, 5, 12))
