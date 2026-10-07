"""Documents that do not match the graph format report only `invalid_document`."""

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import validate_document

from .contract_fixtures import J1, J3, appended, changed, graph_example, step_one_catalog, without
from .graph_checks import found


def j1(path: tuple[str | int, ...], value: JsonValue) -> JsonObject:
    return changed(graph_example(J1), path, value)


CASES: list[tuple[JsonObject, list[tuple[str, str, str | None]]]] = [
    (
        without(graph_example(J1), ("connections",)),
        [("/connections", "Connections is required.", None)],
    ),
    (j1(("format",), "slow-thinker.graph/2"), [("/format", "Format is invalid.", None)]),
    (j1(("id",), "Funny"), [("/id", "Graph identifier has an invalid format.", None)]),
    (
        j1(("limits", "max_activations"), 0),
        [("/limits/max_activations", "Maximum activations must be at least 1.", None)],
    ),
    (
        j1(("limits", "max_running_nodes"), 65),
        [("/limits/max_running_nodes", "Maximum running nodes must be at most 64.", None)],
    ),
    (
        j1(("limits", "time_limit_seconds"), "300"),
        [("/limits/time_limit_seconds", "Time limit has the wrong type.", None)],
    ),
    (
        j1(("limits", "budget_usd"), "0.1234567891"),
        [("/limits/budget_usd", "Budget per run has an invalid format.", None)],
    ),
    (j1(("nodes",), []), [("/nodes", "Nodes is invalid.", None)]),
    (j1(("nodes", 0), 5), [("/nodes/0", "Node has the wrong type.", None)]),
    (
        j1(("nodes", 0, "id"), "Story"),
        [("/nodes/0/id", "Node identifier has an invalid format.", "Story")],
    ),
    (j1(("nodes", 0, "name"), "x" * 81), [("/nodes/0/name", "Node name is too long.", "story")]),
    (
        j1(("nodes", 1, "component"), "llm-call@1"),
        [("/nodes/1/component", "Component has an invalid format.", "proposer")],
    ),
    (
        without(graph_example(J1), ("nodes", 0, "config")),
        [("/nodes/0/config", "Configuration is required.", "story")],
    ),
    (j1(("nodes", 0, "extra"), 1), [("/nodes/0/extra", "Extra is invalid.", "story")]),
    (j1(("extra",), 1), [("/extra", "Extra is invalid.", None)]),
    (
        j1(("connections", 0, "to"), "proposer"),
        [("/connections/0/to", "Connection end has an invalid format.", None)],
    ),
    (
        j1(("layout", "story", 0), 2_000_000),
        [("/layout/story/0", "Layout coordinate must be at most 1000000.", None)],
    ),
    (j1(("layout", "story"), [1, 2, 3]), [("/layout/story", "Layout position is invalid.", None)]),
    (
        changed(graph_example(J3), ("nodes", 2, "embedded", 0, "position"), "input"),
        [
            (
                "/nodes/2/embedded/0/position",
                'Position must be one of "output", "memory".',
                "reviewer",
            )
        ],
    ),
    (j1(("id",), "funny-story\n"), [("/id", "Graph identifier has an invalid format.", None)]),
    (
        j1(("nodes", 0, "id"), "story\n"),
        [("/nodes/0/id", "Node identifier has an invalid format.", "story\n")],
    ),
    (
        j1(("nodes", 1, "component"), "llm-call@1.0.0\n"),
        [("/nodes/1/component", "Component has an invalid format.", "proposer")],
    ),
    (
        j1(("name",), ""),
        [
            ("/name", "Graph name is required.", None),
            ("/name", "Graph name has an invalid format.", None),
        ],
    ),
]


@pytest.mark.parametrize(("document", "expected"), CASES)
def test_schema_violations(
    document: JsonObject, expected: list[tuple[str, str, str | None]]
) -> None:
    assert found(document) == [("invalid_document", *item) for item in expected]


def test_documents_that_are_not_objects() -> None:
    diagnostics = validate_document([], step_one_catalog())
    assert [(item.path, item.message) for item in diagnostics] == [
        ("", "The document has the wrong type.")
    ]


def test_no_other_check_runs_with_schema_violations() -> None:
    document = j1(("nodes", 1, "component"), "llm-call@9.0.0")
    document = appended(document, ("connections",), {"from": "ghost.out", "to": "proposer.in"})
    assert [code for code, *_ in found(document)] == ["unknown_port", "unknown_component"]
    document = changed(document, ("extra",), True)
    assert found(document) == [("invalid_document", "/extra", "Extra is invalid.", None)]
