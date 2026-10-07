"""Graph documents derived from J1 for scheduling cases the journeys do not exercise."""

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object
from slow_thinker_ii.graphs import RunPlan
from support.examples import J1, graph_document, journey_plan, stateful_router, step_one_catalog

ROUTER_SCRIPT = 'def route(received, node_input):\n    return "out", received\n'


def fan_out(workers: int, max_running_nodes: int) -> RunPlan:
    """Story sends to `w1`…`wn` (LLM Call nodes), each sending to the Output."""
    document = graph_document(J1)
    story, proposer, result = _nodes(document)
    names = [f"w{index}" for index in range(1, workers + 1)]
    copies: list[JsonValue] = [{**proposer, "id": name, "name": name.upper()} for name in names]
    document["nodes"] = [story, *copies, result]
    document["connections"] = [
        *(_connection("story.out", f"{name}.in") for name in names),
        *(_connection(f"{name}.out", "result.in") for name in names),
    ]
    document["layout"] = {}
    _limit_running(document, max_running_nodes)
    return journey_plan(document)


def stateful_merge(max_running_nodes: int = 4) -> RunPlan:
    """Story sends to two LLM Calls that both send to `merge`, a stateful Router node."""
    document = graph_document(J1)
    story, proposer, result = _nodes(document)
    merge: JsonObject = {
        "id": "merge",
        "name": "Merge",
        "component": "router@2.0.0",
        "config": {"outputs": ["out"], "script": ROUTER_SCRIPT},
    }
    first: JsonObject = {**proposer, "id": "p1", "name": "First"}
    second: JsonObject = {**proposer, "id": "p2", "name": "Second"}
    document["nodes"] = [story, first, second, merge, result]
    document["connections"] = [
        _connection("story.out", "p1.in"),
        _connection("story.out", "p2.in"),
        _connection("p1.out", "merge.in"),
        _connection("p2.out", "merge.in"),
        _connection("merge.out", "result.in"),
    ]
    document["layout"] = {}
    _limit_running(document, max_running_nodes)
    return journey_plan(document, step_one_catalog(stateful_router()))


def unconnected() -> RunPlan:
    """J1 without the connection from Proposer to the Output."""
    document = graph_document(J1)
    connections = document["connections"]
    assert isinstance(connections, list)
    document["connections"] = connections[:1]
    return journey_plan(document)


def _limit_running(document: JsonObject, max_running_nodes: int) -> None:
    limits = document["limits"]
    assert isinstance(limits, dict)
    limits["max_running_nodes"] = max_running_nodes


def _nodes(document: JsonObject) -> tuple[JsonObject, JsonObject, JsonObject]:
    nodes = document["nodes"]
    assert isinstance(nodes, list)
    story, proposer, result = (json_object(node) for node in nodes)
    return story, proposer, result


def _connection(source: str, target: str) -> JsonValue:
    return {"from": source, "to": target}
