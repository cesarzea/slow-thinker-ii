"""Run plans: the executable form of a valid graph document."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

from slow_thinker_ii.accounting import parse_usd
from slow_thinker_ii.catalog import OUTPUT, TRIGGER, Catalog, ComponentDeclaration, ComponentRef
from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    json_object,
    parse_pointer,
    value_at_pointer,
)

from ._diagnostics import GraphInvalid, has_errors
from ._model import Graph, Node, Part, read_graph
from ._services import selected_entry
from ._validation import validate_document
from ._values import mapping, text

type Port = tuple[str, str]
type Kind = Literal["trigger", "output", "package"]


@dataclass(frozen=True)
class Limits:
    max_activations: int
    max_running_nodes: int
    time_limit_seconds: int
    budget_nanos: int


@dataclass(frozen=True)
class PlanComponent:
    declaration: ComponentDeclaration
    config: JsonObject
    llm_entries: frozenset[str]  # entry ids selected at the component's declared uses


@dataclass(frozen=True)
class PlanNode:
    id: str
    name: str
    kind: Kind
    host: PlanComponent
    embedded_output: PlanComponent | None
    embedded_memory: PlanComponent | None  # a platform Memory: the engine keeps its exchanges
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]  # effective outputs
    stateful: bool  # true if the host or the embedded component is stateful


@dataclass(frozen=True)
class RunPlan:
    graph_id: str
    version: int | None  # None for a change that was never activated
    name: str
    limits: Limits
    nodes: Mapping[str, PlanNode]  # document order
    routes: Mapping[Port, tuple[Port, ...]]  # every effective output, targets in document order
    trigger_id: str

    def node(self, node_id: str) -> PlanNode:
        return self.nodes[node_id]


def compile_plan(document: JsonValue, catalog: Catalog, version: int | None) -> RunPlan:
    """The run plan of a valid document; raises GraphInvalid with all diagnostics otherwise."""
    diagnostics = validate_document(document, catalog)
    if has_errors(diagnostics):
        raise GraphInvalid(diagnostics)
    source = json_object(document)
    graph = read_graph(source, catalog)
    nodes = {node.id: _plan_node(node) for node in graph.nodes}
    return RunPlan(
        graph_id=text(source.get("id")),
        version=version,
        name=text(source.get("name")),
        limits=_limits(mapping(source.get("limits"))),
        nodes=MappingProxyType(nodes),
        routes=MappingProxyType(_routes(graph)),
        trigger_id=next(node.id for node in graph.nodes if node.host.ref == TRIGGER),
    )


def _plan_node(node: Node) -> PlanNode:
    host = _plan_component(node.host)
    output = node.output_part()
    embedded = None if output is None else _plan_component(output)
    remembered = node.embedded_at("memory")
    memory = None if remembered is None else _plan_component(remembered)
    return PlanNode(
        id=node.id,
        name=node.name,
        kind=_kind(node.host.ref),
        host=host,
        embedded_output=embedded,
        embedded_memory=memory,
        inputs=node.inputs() or (),
        outputs=node.outputs() or (),
        stateful=any(part.declaration.stateful for part in (host, embedded, memory) if part),
    )


def _kind(ref: ComponentRef) -> Kind:
    if ref == TRIGGER:
        return "trigger"
    return "output" if ref == OUTPUT else "package"


def _plan_component(part: Part) -> PlanComponent:
    declaration = part.declaration
    assert declaration is not None, "validation guarantees every component is available"
    config = json_object(part.config)
    pointers = (parse_pointer(use.pointer) for use in declaration.uses)
    selections = (selected_entry(value_at_pointer(config, pointer)) for pointer in pointers)
    entries = frozenset(selection[0] for selection in selections if selection is not None)
    return PlanComponent(declaration, config, entries)


def _limits(limits: JsonObject) -> Limits:
    return Limits(
        max_activations=_integer(limits.get("max_activations")),
        max_running_nodes=_integer(limits.get("max_running_nodes")),
        time_limit_seconds=_integer(limits.get("time_limit_seconds")),
        budget_nanos=parse_usd(text(limits.get("budget_usd"))),
    )


def _integer(value: JsonValue) -> int:
    return int(value) if isinstance(value, int | float) else 0


def _routes(graph: Graph) -> dict[Port, tuple[Port, ...]]:
    routes: dict[Port, list[Port]] = {
        (node.id, port): [] for node in graph.nodes for port in node.outputs() or ()
    }
    for connection in graph.connections:
        routes[connection.source].append(connection.target)
    return {source: tuple(targets) for source, targets in routes.items()}
