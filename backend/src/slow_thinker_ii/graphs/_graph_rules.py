"""Graph-wide rules: the Trigger count, the run budget and the warnings."""

from slow_thinker_ii.accounting import parse_usd
from slow_thinker_ii.catalog import OUTPUT, TRIGGER
from slow_thinker_ii.contracts import JsonObject, format_pointer

from ._diagnostics import Diagnostic, error, warning
from ._model import Graph, Node
from ._values import mapping, member, text


def trigger_diagnostics(graph: Graph) -> list[Diagnostic]:
    count = sum(1 for node in graph.nodes if node.host.ref == TRIGGER)
    if count == 1:
        return []
    if count == 0:
        message = "The graph needs a Trigger node."
    else:
        message = f"The graph has {count} Trigger nodes; keep only one."
    return [error("trigger_count", message, "/nodes")]


def limit_diagnostics(graph: Graph) -> list[Diagnostic]:
    budget = text(member(graph.document.get("limits"), "budget_usd"))
    if parse_usd(budget) > 0:
        return []
    message = "Budget per run must be greater than zero."
    return [error("invalid_limits", message, "/limits/budget_usd")]


def warning_diagnostics(graph: Graph) -> list[Diagnostic]:
    targets = {connection.target[0] for connection in graph.connections}
    sources = {connection.source for connection in graph.connections}
    found: list[Diagnostic] = []
    for node in graph.nodes:
        found.extend(_unconnected(node, targets, sources))
    if not any(node.host.ref == OUTPUT for node in graph.nodes):
        message = "The graph has no Output node, so runs produce no results."
        found.append(warning("no_output_node", message, "/nodes"))
    for key in mapping(graph.document.get("layout")):
        if key not in graph.by_id:
            message = f"The layout entry “{key}” does not match a node and is ignored."
            found.append(warning("unknown_layout_node", message, format_pointer(("layout", key))))
    for key, sides in mapping(graph.document.get("port_sides")).items():
        found.extend(_unknown_port_sides(graph, key, mapping(sides)))
    return found


def _unknown_port_sides(graph: Graph, key: str, sides: JsonObject) -> list[Diagnostic]:
    node = graph.by_id.get(key)
    if node is None:
        message = f"The port sides entry “{key}” does not match a node and is ignored."
        return [warning("unknown_port_side", message, format_pointer(("port_sides", key)))]
    inputs, outputs = node.inputs(), node.outputs()
    if inputs is None or outputs is None:
        return []  # the node's ports are unknown while its components are not available
    return [
        warning(
            "unknown_port_side",
            f"{node.name} has no port “{port}”; its side is ignored.",
            format_pointer(("port_sides", key, port)),
            node.id,
        )
        for port in sides
        if port not in (*inputs, *outputs)
    ]


def _unconnected(node: Node, targets: set[str], sources: set[tuple[str, str]]) -> list[Diagnostic]:
    path = format_pointer(("nodes", node.index))
    found: list[Diagnostic] = []
    if node.host.ref != TRIGGER and node.id not in targets:
        message = f"{node.name} has no incoming connection and never runs."
        found.append(warning("unconnected_input", message, path, node.id))
    for port in node.outputs() or ():
        if (node.id, port) not in sources:
            message = (
                f"Output “{port}” of {node.name} is not connected;"
                " messages sent there are discarded."
            )
            found.append(warning("unconnected_output", message, path, node.id))
    return found
