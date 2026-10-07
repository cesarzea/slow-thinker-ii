"""Configured output names and connections between effective ports."""

from slow_thinker_ii.contracts import JsonObject, JsonValue

from .contract_fixtures import J1, J2, appended, changed, graph_example
from .graph_checks import found, found_with

NAMING_RULE = (
    "Names start with a lowercase letter and contain only lowercase letters, digits and"
    " underscores, up to 32 characters."
)
OUTPUTS = "/nodes/1/embedded/0/config/outputs"


def with_router_outputs(outputs: JsonValue) -> JsonObject:
    return changed(graph_example(J2), ("nodes", 1, "embedded", 0, "config", "outputs"), outputs)


def connected(*connections: tuple[str, str]) -> JsonObject:
    document = graph_example(J1)
    for source, target in connections:
        document = appended(document, ("connections",), {"from": source, "to": target})
    return document


def test_invalid_and_repeated_output_names() -> None:
    document = with_router_outputs(["funny", "Not funny", "funny", 5, "not_funny"])
    assert found_with(document, "invalid_port_name") == [
        (
            "invalid_port_name",
            f"{OUTPUTS}/1",
            f"Output names contains “Not funny”, which is not a valid name. {NAMING_RULE}",
            "judge",
        ),
        (
            "invalid_port_name",
            f"{OUTPUTS}/2",
            "Output names contains “funny” more than once.",
            "judge",
        ),
        (
            "invalid_port_name",
            f"{OUTPUTS}/3",
            f"Output names contains 5, which is not a valid name. {NAMING_RULE}",
            "judge",
        ),
    ]
    assert found_with(document, "invalid_config") == []


def test_other_list_problems_remain_configuration_problems() -> None:
    document = with_router_outputs([])
    assert found_with(document, "invalid_config") == [
        ("invalid_config", OUTPUTS, "Output names is invalid.", "judge")
    ]
    assert [code for code, *_ in found(document)] == [
        "unknown_port",
        "unknown_port",
        "invalid_config",
    ]


def test_output_names_of_a_router_node() -> None:
    router: JsonObject = {
        "id": "pick",
        "name": "Pick",
        "component": "router@1.0.0",
        "config": {"outputs": ["a", "a"], "script": "x"},
    }
    document = appended(graph_example(J1), ("nodes",), router)
    assert found_with(document, "invalid_port_name") == [
        (
            "invalid_port_name",
            "/nodes/3/config/outputs/1",
            "Output names contains “a” more than once.",
            "pick",
        )
    ]


def test_connections_to_missing_nodes() -> None:
    document = connected(("ghost.out", "proposer.in"), ("story.out", "ghost.in"))
    assert found_with(document, "unknown_port") == [
        (
            "unknown_port",
            "/connections/2/from",
            "The connection starts at node “ghost”, which does not exist.",
            None,
        ),
        (
            "unknown_port",
            "/connections/3/to",
            "The connection ends at node “ghost”, which does not exist.",
            None,
        ),
    ]


def test_connections_to_missing_ports() -> None:
    document = connected(("proposer.foo", "result.in"), ("story.out", "result.bar"))
    assert found_with(document, "unknown_port") == [
        ("unknown_port", "/connections/2/from", "Proposer has no output “foo”.", "proposer"),
        ("unknown_port", "/connections/3/to", "Funny story has no input “bar”.", "result"),
    ]


def test_connections_in_the_wrong_direction() -> None:
    document = connected(("proposer.in", "result.in"), ("story.out", "proposer.out"))
    assert found_with(document, "wrong_port_direction") == [
        (
            "wrong_port_direction",
            "/connections/2/from",
            "A connection cannot start at the input “in” of Proposer.",
            "proposer",
        ),
        (
            "wrong_port_direction",
            "/connections/3/to",
            "A connection cannot end at the output “out” of Proposer.",
            "proposer",
        ),
    ]


def test_repeated_connections() -> None:
    document = connected(
        ("story.out", "proposer.in"), ("ghost.out", "result.in"), ("ghost.out", "result.in")
    )
    assert found_with(document, "duplicate_connection") == [
        (
            "duplicate_connection",
            "/connections/2",
            "The connection from “story.out” to “proposer.in” is repeated.",
            "story",
        ),
        (
            "duplicate_connection",
            "/connections/4",
            "The connection from “ghost.out” to “result.in” is repeated.",
            None,
        ),
    ]


def test_a_node_may_connect_to_itself() -> None:
    assert found(connected(("proposer.out", "proposer.in"))) == []
