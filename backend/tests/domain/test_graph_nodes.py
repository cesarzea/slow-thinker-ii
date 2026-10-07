"""Node identity, names, component availability, placements and embedding positions."""

from slow_thinker_ii.catalog import Catalog, ComponentDeclaration, parse_declaration
from slow_thinker_ii.contracts import JsonObject, value_at_pointer
from slow_thinker_ii.graphs import validate_document

from .contract_fixtures import J1, J2, appended, changed, declaration_example, graph_example
from .graph_checks import found, found_with

ROUTER_AT_OUTPUT: JsonObject = {
    "position": "output",
    "component": "router@1.0.0",
    "config": {"outputs": ["funny", "not_funny"], "script": "x"},
}


def selector() -> ComponentDeclaration:
    document = changed(declaration_example("router"), ("type",), "selector")
    document = changed(document, ("label",), "Selector")
    return parse_declaration(changed(document, ("placements",), ["output"]))


def test_duplicate_node_identifiers() -> None:
    document = changed(graph_example(J1), ("nodes", 2, "id"), "proposer")
    message = "Node identifier “proposer” is already used by another node."
    assert found_with(document, "duplicate_node_id") == [
        ("duplicate_node_id", "/nodes/2/id", message, "proposer")
    ]


def test_duplicate_node_names_ignore_case() -> None:
    document = changed(graph_example(J1), ("nodes", 2, "name"), "PROPOSER")
    message = "Node name “PROPOSER” is already used by another node."
    assert found(document) == [("duplicate_node_name", "/nodes/2/name", message, "result")]


def test_unknown_host_components_skip_their_dependent_checks() -> None:
    document = changed(graph_example(J1), ("nodes", 1, "component"), "llm-call@2.0.0")
    message = "Component “llm-call@2.0.0” is not installed."
    assert found(document) == [("unknown_component", "/nodes/1/component", message, "proposer")]


def test_unknown_embedded_components() -> None:
    path = ("nodes", 1, "embedded", 0, "component")
    document = changed(graph_example(J2), path, "router@9.0.0")
    message = "Component “router@9.0.0” is not installed."
    assert found(document) == [
        ("unknown_component", "/nodes/1/embedded/0/component", message, "judge")
    ]


def test_components_embedded_where_their_placements_do_not_allow() -> None:
    proposer_config = value_at_pointer(graph_example(J1), ("nodes", 1, "config"))
    embedded: JsonObject = {
        "position": "output",
        "component": "llm-call@1.0.0",
        "config": proposer_config,
    }
    document = changed(graph_example(J1), ("nodes", 1, "embedded"), [embedded])
    message = "LLM Call cannot be embedded at the node's output."
    assert found(document) == [
        ("placement_not_allowed", "/nodes/1/embedded/0/component", message, "proposer")
    ]


def test_components_used_as_nodes_where_their_placements_do_not_allow() -> None:
    node: JsonObject = {"id": "pick", "name": "Pick", "component": "selector@1.0.0", "config": {}}
    document = appended(graph_example(J1), ("nodes",), node)
    message = "Selector cannot be used as a node."
    assert found_with(document, "placement_not_allowed", selector()) == [
        ("placement_not_allowed", "/nodes/3/component", message, "pick")
    ]


def test_one_component_per_embedding_position() -> None:
    document = appended(graph_example(J2), ("nodes", 1, "embedded"), ROUTER_AT_OUTPUT)
    message = "Only one component can be embedded at the node's output."
    assert found(document) == [
        ("duplicate_embedding_position", "/nodes/1/embedded/1/position", message, "judge")
    ]


def test_trigger_nodes_contain_no_embedded_components() -> None:
    document = changed(graph_example(J1), ("nodes", 0, "embedded"), [ROUTER_AT_OUTPUT])
    message = "Trigger nodes cannot contain embedded components."
    assert found_with(document, "placement_not_allowed") == [
        ("placement_not_allowed", "/nodes/0/embedded/0/component", message, "story")
    ]


def test_output_nodes_contain_no_embedded_components() -> None:
    unknown: JsonObject = {"position": "output", "component": "missing@1.0.0", "config": {}}
    document = changed(graph_example(J1), ("nodes", 2, "embedded"), [ROUTER_AT_OUTPUT, unknown])
    message = "Output nodes cannot contain embedded components."
    assert found_with(document, "placement_not_allowed") == [
        ("placement_not_allowed", "/nodes/2/embedded/0/component", message, "result"),
        ("placement_not_allowed", "/nodes/2/embedded/1/component", message, "result"),
    ]
    assert found_with(document, "unknown_component") == []
    assert [path for _, path, *_ in found_with(document, "duplicate_embedding_position")] == [
        "/nodes/2/embedded/1/position"
    ]


def test_platform_host_labels_without_their_declarations() -> None:
    catalog = Catalog([parse_declaration(declaration_example("router"))], [])
    document = changed(graph_example(J1), ("nodes", 0, "embedded"), [ROUTER_AT_OUTPUT])
    placements = [
        (item.path, item.message)
        for item in validate_document(document, catalog)
        if item.code == "placement_not_allowed"
    ]
    message = "Trigger nodes cannot contain embedded components."
    assert placements == [("/nodes/0/embedded/0/component", message)]
