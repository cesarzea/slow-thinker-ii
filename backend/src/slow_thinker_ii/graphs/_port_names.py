"""Output names configured through `outputs_from` that cannot become ports."""

import re
from dataclasses import dataclass

from slow_thinker_ii.catalog import SchemaProblem
from slow_thinker_ii.contracts import JsonValue, encode_json, parse_pointer, value_at_pointer

from ._diagnostics import Diagnostic, error
from ._messages import field_labels
from ._model import Graph, Part
from ._values import items

PORT_NAME = re.compile(r"[a-z][a-z0-9_]{0,31}")
NAMING_RULE = (
    "Names start with a lowercase letter and contain only lowercase letters, digits and"
    " underscores, up to 32 characters."
)


@dataclass(frozen=True)
class NameProblem:
    location: tuple[str, ...]  # of the name inside the component's configuration
    value: JsonValue
    repeated: bool


def name_problems(part: Part) -> list[NameProblem]:
    declaration = part.declaration
    if declaration is None or declaration.outputs_from is None:
        return []
    base = parse_pointer(declaration.outputs_from)
    found: list[NameProblem] = []
    seen: set[str] = set()
    for index, name in enumerate(items(value_at_pointer(part.config, base))):
        location = (*base, str(index))
        if not isinstance(name, str) or PORT_NAME.fullmatch(name) is None:
            found.append(NameProblem(location, name, repeated=False))
        elif name in seen:
            found.append(NameProblem(location, name, repeated=True))
        else:
            seen.add(name)
    return found


def port_name_diagnostics(graph: Graph) -> list[Diagnostic]:
    return [found for node in graph.nodes for part in node.parts() for found in _diagnostics(part)]


def _diagnostics(part: Part) -> list[Diagnostic]:
    declaration = part.declaration
    problems = name_problems(part)
    if declaration is None or not problems:
        return []
    labels = field_labels(declaration)
    found: list[Diagnostic] = []
    for problem in problems:
        label = SchemaProblem.label_of(problem.location[:-1], labels, "Output names")
        message = _message(label, problem)
        path = part.pointer("config", *problem.location)
        found.append(error("invalid_port_name", message, path, part.node_id))
    return found


def _message(label: str, problem: NameProblem) -> str:
    value = problem.value
    shown = f"“{value}”" if isinstance(value, str) else encode_json(value)
    if problem.repeated:
        return f"{label} contains {shown} more than once."
    return f"{label} contains {shown}, which is not a valid name. {NAMING_RULE}"
