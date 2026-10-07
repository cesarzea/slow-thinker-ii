"""Port sides: optional presentation of where each port sits on its node."""

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import compile_plan

from .contract_fixtures import J1, J2, changed, graph_example, step_one_catalog
from .graph_checks import found, found_with

SIDES = 'Port side must be one of "left", "right", "top", "bottom".'


def with_sides(sides: JsonValue, name: str = J1) -> JsonObject:
    return changed(graph_example(name), ("port_sides",), sides)


def test_documents_without_port_sides() -> None:
    assert "port_sides" not in graph_example(J1)
    assert found(graph_example(J1)) == []


def test_sides_of_inputs_outputs_and_embedded_outputs() -> None:
    sides: JsonObject = {
        "story": {"out": "bottom"},
        "proposer": {"in": "top", "out": "right"},
        "result": {"in": "left"},
    }
    assert found(with_sides(sides)) == []
    judge: JsonObject = {"judge": {"in": "left", "funny": "top", "not_funny": "bottom"}}
    assert found(with_sides(judge, J2)) == []


def test_port_sides_never_affect_execution() -> None:
    plain = compile_plan(graph_example(J1), step_one_catalog(), 1)
    sides: JsonObject = {"story": {"out": "bottom"}, "ghost": {"x": "top"}}
    placed = compile_plan(with_sides(sides), step_one_catalog(), 1)
    assert (placed.nodes, placed.routes, placed.limits) == (plain.nodes, plain.routes, plain.limits)


MALFORMED: list[tuple[JsonValue, str, str]] = [
    ({"story": {"out": "middle"}}, "/port_sides/story/out", SIDES),
    ({"story": {"out": 1}}, "/port_sides/story/out", SIDES),
    ("left", "/port_sides", "Port sides has the wrong type."),
    ({"story": "left"}, "/port_sides/story", "Node port sides has the wrong type."),
    ({"story": {"": "left"}}, "/port_sides/story/", "Port name is required."),
    ({"story": {"x" * 41: "left"}}, f"/port_sides/story/{'x' * 41}", "Port name is too long."),
    (
        {"story": {f"p{i}": "left" for i in range(65)}},
        "/port_sides/story",
        "Node port sides is invalid.",
    ),
    ({f"n{i}": {} for i in range(201)}, "/port_sides", "Port sides is invalid."),
]


@pytest.mark.parametrize(("sides", "path", "message"), MALFORMED)
def test_malformed_port_sides_are_errors(sides: JsonValue, path: str, message: str) -> None:
    assert found(with_sides(sides)) == [("invalid_document", path, message, None)]


def test_entries_naming_no_node_or_port_are_ignored_with_a_warning() -> None:
    sides: JsonObject = {"ghost": {"out": "left"}, "proposer": {"in": "top", "foo": "left"}}
    assert found(with_sides(sides)) == [
        (
            "unknown_port_side",
            "/port_sides/ghost",
            "The port sides entry “ghost” does not match a node and is ignored.",
            None,
        ),
        (
            "unknown_port_side",
            "/port_sides/proposer/foo",
            "Proposer has no port “foo”; its side is ignored.",
            "proposer",
        ),
    ]


def test_hidden_host_outputs_and_unavailable_components() -> None:
    hidden = with_sides({"judge": {"out": "right"}}, J2)
    assert [path for _, path, *_ in found_with(hidden, "unknown_port_side")] == [
        "/port_sides/judge/out"
    ]
    unavailable = changed(
        with_sides({"proposer": {"foo": "left"}}), ("nodes", 1, "component"), "x@1.0.0"
    )
    assert found_with(unavailable, "unknown_port_side") == []
