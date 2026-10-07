"""The working copy: draft changes appended in order, listed newest first, keyed by graph."""

import pytest
from slow_thinker_ii.application import ChangeNotFound, GraphInvalid, GraphNotFound
from support.examples import J1, changed, graph_document
from support.platform import Platform

LATER = "2026-10-05T12:01:00.000Z"


def test_changes_are_appended_unless_equal_and_listed_newest_first() -> None:
    platform = Platform()
    platform.library.create(graph_document(J1))
    platform.clock.advance(60)
    renamed = changed(graph_document(J1), ("name",), "Funnier story")
    change, at, created = platform.library.record_change("funny-story", "main", renamed)
    assert (change, created) == (2, True)
    platform.clock.advance(60)
    repeated = platform.library.record_change("funny-story", "main", renamed)
    assert repeated == (2, at, False)
    unfinished = changed(renamed, ("limits", "budget_usd"), "0")
    third = platform.library.record_change("funny-story", "main", unfinished)
    assert (third[0], third[2]) == (3, True)
    listed = platform.library.changes("funny-story")
    assert [(item.change, item.name) for item in listed] == [
        (3, "Funnier story"),
        (2, "Funnier story"),
        (1, "Funny story"),
    ]
    assert [item.change for item in platform.library.changes("funny-story", before=3, limit=1)] == [
        2
    ]
    assert len(platform.library.changes("funny-story", limit=0)) == 1
    assert platform.library.change("funny-story", 2).to_json()["at"] == LATER
    with pytest.raises(ChangeNotFound) as missing:
        platform.library.change("funny-story", 9)
    assert str(missing.value) == "Graph “funny-story” has no change 9."
    [summary] = platform.library.graphs()
    assert (summary.name, summary.latest_change) == ("Funnier story", 3)


def test_a_document_with_reordered_keys_is_a_new_change() -> None:
    platform = Platform()
    platform.library.create(graph_document(J1))
    document = graph_document(J1)
    reordered = {key: document[key] for key in reversed(list(document))}
    change, _, created = platform.library.record_change("funny-story", "main", reordered)
    assert (change, created) == (2, True)
    assert list(platform.library.change("funny-story", 2).document) == list(reordered)
    repeated = platform.library.record_change("funny-story", "main", reordered)
    assert (repeated[0], repeated[2]) == (2, False)


def test_a_change_keeps_the_graph_identifier() -> None:
    platform = Platform()
    platform.library.create(graph_document(J1))
    other = changed(graph_document(J1), ("id",), "another-story")
    with pytest.raises(GraphInvalid) as raised:
        platform.library.record_change("funny-story", "main", other)
    message = "The graph identifier must stay “funny-story”; it cannot change between versions."
    assert [(item.code, item.path, item.message) for item in raised.value.diagnostics] == [
        ("invalid_document", "/id", message)
    ]
    nameless = changed(other, ("name",), "")
    with pytest.raises(GraphInvalid) as raised:
        platform.library.record_change("funny-story", "main", nameless)
    paths = [item.path for item in raised.value.diagnostics]
    assert (paths[0], set(paths)) == ("/id", {"/id", "/name"})
    with pytest.raises(GraphNotFound):
        platform.library.record_change("missing", "main", graph_document(J1))
    with pytest.raises(GraphNotFound):
        platform.library.changes("missing")
