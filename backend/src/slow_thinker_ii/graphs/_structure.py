"""Node identity and naming, component availability and placements."""

from slow_thinker_ii.catalog import OUTPUT, TRIGGER
from slow_thinker_ii.contracts import format_pointer

from ._diagnostics import Diagnostic, error
from ._model import Graph, Node, Part

PLATFORM = (TRIGGER, OUTPUT)


def identity_diagnostics(graph: Graph) -> list[Diagnostic]:
    found: list[Diagnostic] = []
    identifiers: set[str] = set()
    names: set[str] = set()
    for node in graph.nodes:
        if node.id in identifiers:
            message = f"Node identifier “{node.id}” is already used by another node."
            path = format_pointer(("nodes", node.index, "id"))
            found.append(error("duplicate_node_id", message, path, node.id))
        if node.name.casefold() in names:
            message = f"Node name “{node.name}” is already used by another node."
            path = format_pointer(("nodes", node.index, "name"))
            found.append(error("duplicate_node_name", message, path, node.id))
        identifiers.add(node.id)
        names.add(node.name.casefold())
    return found


def component_diagnostics(graph: Graph) -> list[Diagnostic]:
    found: list[Diagnostic] = []
    for node in graph.nodes:
        found.extend(_placement(node.host, "node"))
        positions: set[str] = set()
        for position, part in node.embedded:
            if position in positions:
                message = f"Only one component can be embedded at the node's {position}."
                found.append(
                    error(
                        "duplicate_embedding_position", message, part.pointer("position"), node.id
                    )
                )
            positions.add(position)
            found.extend(_embedding(node, part, position))
    return found


def _embedding(node: Node, part: Part, position: str) -> list[Diagnostic]:
    """Platform nodes accept no embedded components; this replaces the component's own checks."""
    if node.host.ref not in PLATFORM:
        return _placement(part, position)
    host = node.host.declaration
    label = node.host.ref.type.capitalize() if host is None else host.label
    message = f"{label} nodes cannot contain embedded components."
    return [error("placement_not_allowed", message, part.pointer("component"), node.id)]


def _placement(part: Part, placement: str) -> list[Diagnostic]:
    path = part.pointer("component")
    declaration = part.declaration
    if declaration is None:
        message = f"Component “{part.component}” is not installed."
        return [error("unknown_component", message, path, part.node_id)]
    if placement in declaration.placements:
        return []
    usage = "used as a node" if placement == "node" else f"embedded at the node's {placement}"
    message = f"{declaration.label} cannot be {usage}."
    return [error("placement_not_allowed", message, path, part.node_id)]
