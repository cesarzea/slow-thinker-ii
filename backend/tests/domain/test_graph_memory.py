"""A Memory goes only at a node's memory position, beside an output component if any."""

from slow_thinker_ii.contracts import JsonObject
from support.examples import memory_declaration

from .contract_fixtures import J1, J2, appended, changed, graph_example
from .graph_checks import found, found_with

AT_MEMORY: JsonObject = {
    "position": "memory",
    "component": "memory@1.0.0",
    "config": {"max_exchanges": 3},
}


def test_a_memory_goes_beside_a_router() -> None:
    document = appended(graph_example(J2), ("nodes", 1, "embedded"), AT_MEMORY)
    assert found(document, memory_declaration()) == []


def test_a_memory_is_not_an_output_component() -> None:
    at_output = {**AT_MEMORY, "position": "output"}
    document = changed(graph_example(J1), ("nodes", 1, "embedded"), [at_output])
    assert found_with(document, "placement_not_allowed", memory_declaration()) == [
        (
            "placement_not_allowed",
            "/nodes/1/embedded/0/component",
            "Memory cannot be embedded at the node's output.",
            "proposer",
        )
    ]


def test_a_router_is_not_a_memory() -> None:
    document = changed(graph_example(J2), ("nodes", 1, "embedded", 0, "position"), "memory")
    assert found_with(document, "placement_not_allowed", memory_declaration()) == [
        (
            "placement_not_allowed",
            "/nodes/1/embedded/0/component",
            "Router cannot be embedded at the node's memory.",
            "judge",
        )
    ]


def test_a_memory_is_not_a_node() -> None:
    node: JsonObject = {"id": "keep", "name": "Keep", "component": "memory@1.0.0", "config": {}}
    document = appended(graph_example(J1), ("nodes",), node)
    message = "Memory cannot be used as a node."
    expected = ("placement_not_allowed", "/nodes/3/component", message, "keep")
    assert expected in found(document, memory_declaration())
