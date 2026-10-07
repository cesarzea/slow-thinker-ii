"""Branches: each with its own working copy and lineage of versions; numbers are per graph."""

import pytest
from slow_thinker_ii.application import (
    BranchExists,
    BranchNotFound,
    ChangeNotFound,
    GraphLibrary,
    GraphNotFound,
    InvalidBranch,
    VersionNotFound,
)
from support.examples import J1, changed, graph_document
from support.platform import Platform

GRAPH = "funny-story"


def test_a_branch_from_a_version_activates_on_its_own_lineage() -> None:
    platform = Platform()
    library = platform.library
    library.create(graph_document(J1))
    first = library.activate(GRAPH, 1)
    library.record_change(GRAPH, "main", changed(graph_document(J1), ("name",), "Funnier story"))
    second = library.activate(GRAPH, 2)
    start = library.create_branch(GRAPH, "experiment", from_version=1)
    assert start == 3
    assert library.change(GRAPH, 3).document == graph_document(J1)
    richer = changed(graph_document(J1), ("limits", "budget_usd"), "0.20")
    library.record_change(GRAPH, "experiment", richer)
    third, fourth = library.activate(GRAPH, 4), library.activate(GRAPH, 4)
    lineage = [(item.version, item.branch, item.parent) for item in (first, second, third, fourth)]
    assert lineage == [
        (1, "main", None),
        (2, "main", 1),
        (3, "experiment", 1),
        (4, "experiment", 3),
    ]


def test_branch_summaries_and_changes_follow_each_branch() -> None:
    platform = Platform()
    library = _two_branches(platform)
    record = library.graph(GRAPH)
    assert (record.active_version, record.latest_change) == (4, 4)
    summaries = [
        (item.name, item.from_version, item.from_change, item.latest_change, item.head_version)
        for item in library.branches(GRAPH)
    ]
    assert summaries == [("main", None, None, 2, 2), ("experiment", 1, None, 4, 4)]
    assert [item.change for item in library.changes(GRAPH, "experiment")] == [4, 3]
    every = library.changes(GRAPH)
    assert [(item.change, item.branch) for item in every] == [
        (4, "experiment"),
        (3, "experiment"),
        (2, "main"),
        (1, "main"),
    ]
    version = library.version(GRAPH, 3)
    assert (version.branch, version.parent, version.change) == ("experiment", 1, 4)


def test_a_branch_from_a_change_has_no_parent_before_its_first_version() -> None:
    platform = Platform()
    library = platform.library
    library.create(graph_document(J1))
    start = library.create_branch(GRAPH, "Try 2.1_b-c", from_change=1)
    activated = library.activate(GRAPH, start)
    assert (activated.version, activated.branch, activated.parent) == (1, "Try 2.1_b-c", None)
    branch = library.branches(GRAPH)[1]
    assert (branch.from_version, branch.from_change, branch.head_version) == (None, 1, 1)


def test_branch_names_follow_the_rule_and_are_unique_ignoring_case() -> None:
    platform = Platform()
    library = platform.library
    library.create(graph_document(J1))
    for name in ("", " lead", "-lead", "x" * 41, "bad/name", "ñame"):
        with pytest.raises(InvalidBranch, match="A branch name has 1 to 40"):
            library.create_branch(GRAPH, name, from_change=1)
    with pytest.raises(BranchExists) as raised:
        library.create_branch(GRAPH, "MAIN", from_change=1)
    assert str(raised.value) == "Graph “funny-story” already has a branch named “MAIN”."
    with pytest.raises(InvalidBranch, match="either a version or a change"):
        library.create_branch(GRAPH, "both", from_version=1, from_change=1)
    with pytest.raises(InvalidBranch, match="either a version or a change"):
        library.create_branch(GRAPH, "neither")
    with pytest.raises(VersionNotFound):
        library.create_branch(GRAPH, "later", from_version=9)
    with pytest.raises(ChangeNotFound):
        library.create_branch(GRAPH, "later", from_change=9)
    assert len(library.branches(GRAPH)) == 1


def test_changes_are_deduplicated_against_their_own_branch() -> None:
    platform = Platform()
    library = platform.library
    library.create(graph_document(J1))
    library.create_branch(GRAPH, "copy", from_change=1)
    same_on_main = library.record_change(GRAPH, "main", graph_document(J1))
    same_on_copy = library.record_change(GRAPH, "copy", graph_document(J1))
    assert (same_on_main[0], same_on_main[2], same_on_copy[0], same_on_copy[2]) == (
        1,
        False,
        2,
        False,
    )
    renamed = changed(graph_document(J1), ("name",), "Funnier story")
    on_copy = library.record_change(GRAPH, "copy", renamed)
    on_main = library.record_change(GRAPH, "main", renamed)
    assert ((on_copy[0], on_copy[2]), (on_main[0], on_main[2])) == ((3, True), (4, True))
    with pytest.raises(BranchNotFound) as missing:
        library.record_change(GRAPH, "nope", renamed)
    assert str(missing.value) == "Graph “funny-story” has no branch “nope”."
    with pytest.raises(BranchNotFound):
        library.changes(GRAPH, "nope")
    with pytest.raises(GraphNotFound):
        library.branches("missing")


def _two_branches(platform: Platform) -> GraphLibrary:
    """`main` with versions 1 and 2; `experiment` from version 1 with versions 3 and 4."""
    library = platform.library
    library.create(graph_document(J1))
    library.activate(GRAPH, 1)
    library.record_change(GRAPH, "main", changed(graph_document(J1), ("name",), "Funnier story"))
    library.activate(GRAPH, 2)
    library.create_branch(GRAPH, "experiment", from_version=1)
    richer = changed(graph_document(J1), ("limits", "budget_usd"), "0.20")
    library.record_change(GRAPH, "experiment", richer)
    library.activate(GRAPH, 4)
    library.activate(GRAPH, 4)
    return library
