"""Typed view of a schema-valid graph document, with components resolved in a catalog."""

from collections.abc import Mapping
from dataclasses import dataclass

from slow_thinker_ii.catalog import Catalog, ComponentDeclaration, ComponentRef
from slow_thinker_ii.contracts import JsonObject, JsonValue, format_pointer

from ._values import items, mapping, member, text

type Path = tuple[str | int, ...]


@dataclass(frozen=True)
class Part:
    """A component placed in a graph: a node's host or one of its embedded components."""

    path: Path
    node_id: str
    component: str
    ref: ComponentRef
    config: JsonObject
    declaration: ComponentDeclaration | None

    def pointer(self, *tokens: str | int) -> str:
        return format_pointer((*self.path, *tokens))


@dataclass(frozen=True)
class Node:
    index: int
    id: str
    name: str
    host: Part
    embedded: tuple[tuple[str, Part], ...]

    def parts(self) -> tuple[Part, ...]:
        return (self.host, *(part for _, part in self.embedded))

    def output_part(self) -> Part | None:
        return self.embedded_at("output")

    def embedded_at(self, position: str) -> Part | None:
        return next((part for at, part in self.embedded if at == position), None)

    def inputs(self) -> tuple[str, ...] | None:
        declaration = self.host.declaration
        return None if declaration is None else declaration.inputs

    def outputs(self) -> tuple[str, ...] | None:
        """Effective outputs; None when the component providing them is not available."""
        provider = self.output_part() or self.host
        declaration = provider.declaration
        return None if declaration is None else declaration.output_ports(provider.config)


@dataclass(frozen=True)
class Connection:
    index: int
    source: tuple[str, str]
    target: tuple[str, str]


@dataclass(frozen=True)
class Graph:
    document: JsonObject
    nodes: tuple[Node, ...]
    connections: tuple[Connection, ...]
    by_id: Mapping[str, Node]  # the first node with each identifier


def read_graph(document: JsonObject, catalog: Catalog) -> Graph:
    nodes = tuple(
        _node(index, mapping(item), catalog)
        for index, item in enumerate(items(document.get("nodes")))
    )
    connections = tuple(
        Connection(index, _endpoint(member(item, "from")), _endpoint(member(item, "to")))
        for index, item in enumerate(items(document.get("connections")))
    )
    return Graph(document, nodes, connections, {node.id: node for node in reversed(nodes)})


def _node(index: int, item: JsonObject, catalog: Catalog) -> Node:
    node_id = text(item.get("id"))
    path: Path = ("nodes", index)
    embedded = tuple(
        (
            text(member(entry, "position")),
            _part((*path, "embedded", order), node_id, entry, catalog),
        )
        for order, entry in enumerate(items(item.get("embedded")))
    )
    host = _part(path, node_id, item, catalog)
    return Node(index, node_id, text(item.get("name")), host, embedded)


def _part(path: Path, node_id: str, item: JsonValue, catalog: Catalog) -> Part:
    fields = mapping(item)
    component = text(fields.get("component"))
    ref = ComponentRef.parse(component)  # the document's JSON Schema has checked the reference
    config = mapping(fields.get("config"))
    return Part(path, node_id, component, ref, config, catalog.component(ref))


def _endpoint(value: JsonValue) -> tuple[str, str]:
    node_id, _, port = text(value).partition(".")
    return node_id, port
