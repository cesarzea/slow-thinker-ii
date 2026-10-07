"""The graph library: a working copy of draft changes, and versions activated from them."""

import pytest
from slow_thinker_ii.application import (
    ChangeNotFound,
    GraphExists,
    GraphInvalid,
    GraphNotFound,
    VersionNotFound,
)
from slow_thinker_ii.contracts import JsonObject, JsonValue
from support.examples import J1, changed, graph_document
from support.platform import Platform

DRAFT: JsonObject = {"format": "slow-thinker.graph/1", "id": "draft", "name": "Draft"}
LATER = "2026-10-05T12:01:00.000Z"


def test_validation_returns_diagnostics_and_stores_nothing() -> None:
    platform = Platform()
    assert platform.library.validate(graph_document(J1)) == ()
    invalid = changed(graph_document(J1), ("limits", "budget_usd"), "0")
    assert [item.code for item in platform.library.validate(invalid)] == ["invalid_limits"]
    assert platform.library.graphs() == ()


def test_a_graph_starts_as_change_one_of_a_draft_without_versions() -> None:
    platform = Platform()
    created = platform.library.create(DRAFT)
    assert created == ("draft", "main", 1)
    with pytest.raises(GraphExists) as raised:
        platform.library.create(DRAFT)
    assert str(raised.value) == "A graph with the identifier “draft” already exists."
    record = platform.library.graph("draft")
    assert (record.name, record.active_version, record.latest_change) == ("Draft", None, 1)
    assert record.versions == ()
    [main] = record.branches
    assert (main.name, main.from_version, main.latest_change, main.head_version) == (
        "main",
        None,
        1,
        None,
    )
    [summary] = platform.library.graphs()
    assert (summary.active_version, summary.latest_change) == (None, 1)


@pytest.mark.parametrize(
    ("document", "path"),
    [
        ([], ""),
        ({**DRAFT, "format": "slow-thinker.graph/2"}, "/format"),
        ({**DRAFT, "id": "Draft One"}, "/id"),
        ({"format": "slow-thinker.graph/1", "id": "draft"}, "/name"),
        ({**DRAFT, "name": "   "}, "/name"),
        ({**DRAFT, "notes": "x" * 1_048_576}, ""),
    ],
)
def test_drafts_need_a_format_an_identifier_a_name_and_a_bounded_size(
    document: JsonValue, path: str
) -> None:
    platform = Platform()
    with pytest.raises(GraphInvalid) as raised:
        platform.library.create(document)
    assert [item.path for item in raised.value.diagnostics] == [path]
    assert platform.library.graphs() == ()


def test_activation_creates_the_next_version_from_a_valid_change() -> None:
    platform = Platform()
    platform.library.create(graph_document(J1))
    renamed = changed(graph_document(J1), ("name",), "Funnier story")
    platform.library.record_change("funny-story", "main", renamed)
    unfinished = changed(renamed, ("limits", "budget_usd"), "0")
    platform.library.record_change("funny-story", "main", unfinished)
    versions = [platform.library.activate("funny-story", change) for change in (1, 2)]
    assert [(item.version, item.branch, item.parent) for item in versions] == [
        (1, "main", None),
        (2, "main", 1),
    ]
    with pytest.raises(GraphInvalid) as raised:
        platform.library.activate("funny-story", 3)
    assert [item.code for item in raised.value.diagnostics] == ["invalid_limits"]
    with pytest.raises(ChangeNotFound):
        platform.library.activate("funny-story", 9)


def test_versions_record_their_change_branch_and_parent() -> None:
    platform = Platform()
    platform.library.create(graph_document(J1))
    renamed = changed(graph_document(J1), ("name",), "Funnier story")
    platform.library.record_change("funny-story", "main", renamed)
    platform.library.record_change("funny-story", "main", changed(renamed, ("name",), "Third"))
    for change in (1, 2):
        platform.library.activate("funny-story", change)
    record = platform.library.graph("funny-story")
    assert (record.active_version, record.latest_change) == (2, 3)
    assert [(item.version, item.change, item.name) for item in record.versions] == [
        (1, 1, "Funny story"),
        (2, 2, "Funnier story"),
    ]
    assert record.branches[0].head_version == 2
    version = platform.library.version("funny-story", 2)
    assert (version.change, version.branch, version.parent, version.document) == (
        2,
        "main",
        1,
        renamed,
    )
    assert [item.version for item in platform.library.changes("funny-story")] == [None, 2, 1]
    again = platform.library.activate("funny-story", 1)
    assert (again.version, again.parent) == (3, 2)
    assert platform.library.change("funny-story", 1).version == 3
    with pytest.raises(VersionNotFound):
        platform.library.version("funny-story", 9)
    with pytest.raises(GraphNotFound):
        platform.library.graph("missing")
