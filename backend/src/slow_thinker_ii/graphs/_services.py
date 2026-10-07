"""Service selections at declared uses, checked against the LLM catalog."""

from slow_thinker_ii.catalog import (
    Catalog,
    ComponentDeclaration,
    LlmEntry,
    SchemaProblem,
    ServiceUse,
    schema_problems,
)
from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    format_pointer,
    parse_pointer,
    value_at_pointer,
)

from ._diagnostics import Diagnostic, error
from ._messages import field_labels
from ._model import Graph, Part


def service_diagnostics(
    graph: Graph, catalog: Catalog, reported: frozenset[str]
) -> list[Diagnostic]:
    """Diagnostics of every declared use; `reported` holds paths with invalid_config already."""
    found: list[Diagnostic] = []
    for node in graph.nodes:
        for part in node.parts():
            declaration = part.declaration
            if declaration is not None:
                for use in declaration.uses:
                    found.extend(_selection(part, declaration, use, catalog, reported))
    return found


def selected_entry(value: JsonValue) -> tuple[str, JsonObject] | None:
    """The entry identifier and parameters of a well-formed selection."""
    if not isinstance(value, dict) or set(value) != {"llm", "parameters"}:
        return None
    entry, parameters = value["llm"], value["parameters"]
    if not isinstance(entry, str) or not isinstance(parameters, dict):
        return None
    return entry, parameters


def _selection(
    part: Part,
    declaration: ComponentDeclaration,
    use: ServiceUse,
    catalog: Catalog,
    reported: frozenset[str],
) -> list[Diagnostic]:
    location = parse_pointer(use.pointer)
    value = value_at_pointer(part.config, location)
    path = part.pointer("config", *location)
    if value is None:
        return [error("service_not_selected", "Select a model.", path, part.node_id)]
    selection = selected_entry(value)
    if selection is None:
        return [] if path in reported else [_malformed(part, declaration, location)]
    entry_id, parameters = selection
    entry = catalog.llm(entry_id)
    if entry is None:
        message = f"Model “{entry_id}” is not available; select another model."
        return [error("unknown_service_entry", message, f"{path}/llm", part.node_id)]
    return _parameters(part, path, entry, parameters)


def _malformed(
    part: Part, declaration: ComponentDeclaration, location: tuple[str, ...]
) -> Diagnostic:
    label = SchemaProblem.label_of(location, field_labels(declaration), "Configuration")
    path = part.pointer("config", *location)
    return error("invalid_config", f"{label} is invalid.", path, part.node_id)


def _parameters(part: Part, path: str, entry: LlmEntry, parameters: JsonObject) -> list[Diagnostic]:
    found: list[Diagnostic] = []
    for problem in schema_problems(entry.parameters, parameters, fallback="Parameters"):
        where = f"{path}/parameters{format_pointer(problem.path)}"
        found.append(error("invalid_service_parameters", problem.sentence, where, part.node_id))
    return found
