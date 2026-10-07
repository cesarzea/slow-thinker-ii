"""Connections between effective ports."""

from typing import Literal

from slow_thinker_ii.contracts import format_pointer

from ._diagnostics import Diagnostic, error
from ._model import Connection, Graph

type End = Literal["from", "to"]


def connection_diagnostics(graph: Graph) -> list[Diagnostic]:
    found: list[Diagnostic] = []
    seen: set[tuple[tuple[str, str], tuple[str, str]]] = set()
    for connection in graph.connections:
        found.extend(_endpoint(graph, connection.index, "from", connection.source))
        found.extend(_endpoint(graph, connection.index, "to", connection.target))
        if (connection.source, connection.target) in seen:
            found.append(_repeated(graph, connection))
        seen.add((connection.source, connection.target))
    return found


def _endpoint(graph: Graph, index: int, end: End, endpoint: tuple[str, str]) -> list[Diagnostic]:
    node_id, port = endpoint
    path = format_pointer(("connections", index, end))
    starts = end == "from"
    verb = "start" if starts else "end"
    node = graph.by_id.get(node_id)
    if node is None:
        message = f"The connection {verb}s at node “{node_id}”, which does not exist."
        return [error("unknown_port", message, path)]
    own, other = (node.outputs(), node.inputs()) if starts else (node.inputs(), node.outputs())
    if own is None or port in own:
        return []
    own_kind, other_kind = ("output", "input") if starts else ("input", "output")
    if other is not None and port in other:
        message = f"A connection cannot {verb} at the {other_kind} “{port}” of {node.name}."
        return [error("wrong_port_direction", message, path, node.id)]
    return [error("unknown_port", f"{node.name} has no {own_kind} “{port}”.", path, node.id)]


def _repeated(graph: Graph, connection: Connection) -> Diagnostic:
    source, target = ".".join(connection.source), ".".join(connection.target)
    node = graph.by_id.get(connection.source[0])
    message = f"The connection from “{source}” to “{target}” is repeated."
    path = format_pointer(("connections", connection.index))
    return error("duplicate_connection", message, path, None if node is None else node.id)
