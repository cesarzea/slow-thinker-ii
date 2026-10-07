"""JSON Schema validation of the graph document format, reported as `invalid_document`."""

from importlib.resources import files

from slow_thinker_ii.catalog import SchemaProblem, schema_problems
from slow_thinker_ii.contracts import (
    JsonValue,
    decode_json,
    format_pointer,
    json_object,
    value_at_pointer,
)

from ._diagnostics import Diagnostic, error
from ._values import INDEX

GRAPH_SCHEMA = "graph-document-1.schema.json"
_KEYED = (("layout", 1), ("port_sides", 2))  # leading members keyed by names, not fields
_LABELS = (
    ("", "The document"),
    ("format", "Format"),
    ("id", "Graph identifier"),
    ("name", "Graph name"),
    ("limits", "Limits"),
    ("limits/max_activations", "Maximum activations"),
    ("limits/max_running_nodes", "Maximum running nodes"),
    ("limits/time_limit_seconds", "Time limit"),
    ("limits/budget_usd", "Budget per run"),
    ("nodes", "Nodes"),
    ("nodes/#", "Node"),
    ("nodes/#/id", "Node identifier"),
    ("nodes/#/name", "Node name"),
    ("nodes/#/component", "Component"),
    ("nodes/#/config", "Configuration"),
    ("nodes/#/embedded", "Embedded components"),
    ("nodes/#/embedded/#", "Embedded component"),
    ("nodes/#/embedded/#/position", "Position"),
    ("nodes/#/embedded/#/component", "Component"),
    ("nodes/#/embedded/#/config", "Configuration"),
    ("connections", "Connections"),
    ("connections/#", "Connection"),
    ("connections/#/from", "Connection start"),
    ("connections/#/to", "Connection end"),
    ("view", "View"),
    ("view/connections", "Connection style"),
    ("view/curvature", "Curvature"),
    ("view/observe", "Observed points"),
    ("port_sides", "Port sides"),
    ("port_sides/*", "Node port sides"),
    ("port_sides/*/*", "Port side"),
    ("layout", "Layout"),
    ("layout/*", "Layout position"),
    ("layout/*/#", "Layout coordinate"),
)


def document_diagnostics(document: JsonValue) -> list[Diagnostic]:
    resource = files("slow_thinker_ii.graphs").joinpath("_data", GRAPH_SCHEMA)
    schema = json_object(decode_json(resource.read_text(encoding="utf-8")))
    problems = schema_problems(schema, document, labels=())
    return [_invalid(document, problem) for problem in problems]


def _invalid(document: JsonValue, problem: SchemaProblem) -> Diagnostic:
    path = problem.path
    label = _label(path, problem.keyword)
    message = problem.sentence if label is None else f"{label} {problem.phrase}."
    return error("invalid_document", message, format_pointer(path), _node_id(document, path))


def _label(path: tuple[str, ...], keyword: str) -> str | None:
    """The label of a graph document field; None for values the table does not name."""
    keyed = next((depth for name, depth in _KEYED if path[:1] == (name,)), 0)
    shape = "/".join(
        "*" if 0 < index <= keyed else "#" if INDEX.fullmatch(token) else token
        for index, token in enumerate(path)
    )
    if shape == "port_sides/*/*" and keyword in ("minLength", "maxLength"):
        return "Port name"  # refused by `propertyNames`: the name, not the side
    return next((label for known, label in _LABELS if known == shape), None)


def _node_id(document: JsonValue, location: tuple[str, ...]) -> str | None:
    if len(location) < 2 or location[0] != "nodes":
        return None
    node_id = value_at_pointer(document, ("nodes", location[1], "id"))
    return node_id if isinstance(node_id, str) else None
