"""Coordinate definition-only graph validation and immutable record projection."""

from pathlib import Path

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, encode_json
from slow_thinker_ii.definitions import GraphSummary, PlannedNode, graph_input_schema

from .._models import GraphRecord
from ._diagnostics import require
from ._nodes import nodes
from ._references import compositions, containment, controller, permissions, resources
from ._schemas import LocalSchemas
from ._types import instances


def validate_definition(
    value: JsonObject, schemas: LocalSchemas, directory: Path, extra: tuple[str, ...] = ()
) -> tuple[library.ValidatedDefinition, dict[str, tuple[str, ...]]]:
    schemas.validate(value, schemas.graph, ())
    graph = GraphRecord.model_validate(value)
    schemas.schema(graph_input_schema(value), "/input_schema")
    resolved = instances(graph, directory, schemas, extra)
    containment(graph)
    controller(graph, resolved)
    allowed = permissions(graph, resolved)
    resources(graph, resolved, allowed)
    compositions(graph, resolved, allowed)
    steps = nodes(graph, resolved, schemas)
    return document(graph, value, steps), {
        identity: item.roles for identity, item in resolved.items()
    }


def document(
    graph: GraphRecord, value: JsonObject, steps: tuple[str, ...]
) -> library.ValidatedDefinition:
    reference = library.GraphReference(graph.graph_id, graph.revision)
    parent = (
        None
        if graph.derived_from is None
        else library.GraphReference(
            str(graph.derived_from["graph_id"]), str(graph.derived_from["revision"])
        )
    )
    require(parent != reference, "/derived_from", "A definition cannot derive from itself.")
    summary = GraphSummary(
        graph.graph_id,
        graph.revision,
        tuple(PlannedNode(identity, graph.nodes[identity].component) for identity in steps),
        encode_json(graph_input_schema(value)),
    )
    return library.ValidatedDefinition(reference, encode_json(value), parent, summary)
