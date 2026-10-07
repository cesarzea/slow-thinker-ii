"""Branches: started from a version or a change, unique ignoring case, each with its own copy."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteGraphStore
from slow_thinker_ii.application import (
    BranchExists,
    BranchSummary,
    ChangeRecord,
    GraphNotFound,
    VersionSummary,
)
from slow_thinker_ii.contracts import JsonObject

from .stores import AT, initialized, later


def document(name: str) -> JsonObject:
    return {"format": "slow-thinker.graph/1", "id": "g", "name": name}


def graph_with_version(directory: Path) -> SqliteGraphStore:
    """Graph `g`: changes 1 and 2 on main, version 1 from change 2."""
    store = SqliteGraphStore(initialized(directory))
    store.create("g", "First", document("First"), AT)
    store.add_change("g", "main", "Second", document("Second"), later(1))
    store.add_version("g", 2, None, later(2))
    return store


def test_branches_start_from_a_version_or_a_change(tmp_path: Path) -> None:
    store = graph_with_version(tmp_path)
    assert store.create_branch("g", "Shorter", "Second", document("Second"), 1, 2, later(3)) == 3
    assert store.create_branch("g", "idea 2", "First", document("First"), None, 1, later(4)) == 4
    assert store.branches("g") == (
        BranchSummary("main", AT, None, None, 2, 1),
        BranchSummary("Shorter", later(3), 1, 2, 3, None),
        BranchSummary("idea 2", later(4), None, 1, 4, None),
    )
    first = store.latest_change("g", "idea 2")
    assert first == ChangeRecord("g", 4, "idea 2", later(4), document("First"), None)
    assert [(item.change, item.branch) for item in store.changes("g", None, None, 10)] == [
        (4, "idea 2"),
        (3, "Shorter"),
        (2, "main"),
        (1, "main"),
    ]
    assert [item.change for item in store.changes("g", "Shorter", None, 10)] == [3]


def test_branch_names_are_unique_ignoring_case(tmp_path: Path) -> None:
    store = graph_with_version(tmp_path)
    store.create_branch("g", "Größe", "First", document("First"), None, 1, later(3))
    for taken in ("MAIN", "main", "GRÖSSE", "größe"):
        with pytest.raises(BranchExists):
            store.create_branch("g", taken, "First", document("First"), None, 1, later(4))
    with pytest.raises(GraphNotFound):
        store.create_branch("missing", "x", "First", document("First"), None, 1, later(4))
    assert [branch.name for branch in store.branches("g")] == ["main", "Größe"]
    assert store.change("g", 4) is None


def test_dedupe_compares_with_the_latest_change_of_the_same_branch(tmp_path: Path) -> None:
    store = graph_with_version(tmp_path)
    store.create_branch("g", "copy", "First", document("First"), None, 1, later(3))
    assert store.add_change("g", "copy", "First", document("First"), later(4)) == 3
    assert store.add_change("g", "main", "First", document("First"), later(5)) == 4
    assert store.add_change("g", "copy", "Second", document("Second"), later(6)) == 5
    assert store.add_change("g", "main", "First", document("First"), later(7)) == 4


def test_versions_record_their_branch_and_lineage(tmp_path: Path) -> None:
    store = graph_with_version(tmp_path)
    store.create_branch("g", "copy", "Second", document("Second"), 1, 2, later(3))
    store.add_change("g", "copy", "Third", document("Third"), later(4))
    assert store.add_version("g", 4, 1, later(5)) == 2  # follows the version it started from
    assert store.add_version("g", 2, 1, later(6)) == 3  # main goes on from its own head
    record = store.graph("g")
    assert record is not None and record.versions == (
        VersionSummary(1, "main", None, 2, "Second", later(2)),
        VersionSummary(2, "copy", 1, 4, "Third", later(5)),
        VersionSummary(3, "main", 1, 2, "Second", later(6)),
    )
    assert [(item.name, item.head_version) for item in record.branches] == [
        ("main", 3),
        ("copy", 2),
    ]
    assert (record.active_version, record.latest_change, record.name) == (3, 4, "Third")
    version = store.version("g", 2)
    assert version is not None and (version.branch, version.parent, version.change) == (
        "copy",
        1,
        4,
    )
