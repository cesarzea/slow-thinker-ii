"""Configuration checked against each component's configuration schema."""

from slow_thinker_ii.catalog import ComponentDeclaration, SchemaProblem, schema_problems
from slow_thinker_ii.contracts import parse_pointer, value_at_pointer

from ._diagnostics import Diagnostic, error
from ._messages import field_labels
from ._model import Graph, Part
from ._port_names import name_problems

type Location = tuple[str, ...]


def configuration_diagnostics(graph: Graph) -> list[Diagnostic]:
    found: list[Diagnostic] = []
    for node in graph.nodes:
        for part in node.parts():
            if part.declaration is not None:
                found.extend(_part_diagnostics(part, part.declaration))
    return found


def _part_diagnostics(part: Part, declaration: ComponentDeclaration) -> list[Diagnostic]:
    # Values reported with a more specific code are not also reported as invalid_config:
    # unselected services (service_not_selected) and output names (invalid_port_name).
    problems = name_problems(part)
    covered = {problem.location for problem in problems} | _unselected(part, declaration)
    repeated = {problem.location[:-1] for problem in problems if problem.repeated}
    labels = field_labels(declaration)
    found: list[Diagnostic] = []
    for problem in schema_problems(declaration.config_schema, part.config, labels, "Configuration"):
        if _reported(problem, covered, repeated):
            path = part.pointer("config", *problem.path)
            found.append(error("invalid_config", problem.sentence, path, part.node_id))
    return found


def _unselected(part: Part, declaration: ComponentDeclaration) -> set[Location]:
    locations = (parse_pointer(use.pointer) for use in declaration.uses)
    return {location for location in locations if value_at_pointer(part.config, location) is None}


def _reported(problem: SchemaProblem, covered: set[Location], repeated: set[Location]) -> bool:
    if problem.path in covered:
        return False
    return not (problem.keyword == "uniqueItems" and problem.path in repeated)
