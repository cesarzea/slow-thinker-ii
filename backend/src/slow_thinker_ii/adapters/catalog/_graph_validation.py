"""Graph-wide validation shared by finite and conditional compilation."""

from slow_thinker_ii.contracts import JsonObject, encode_json

from ._models import GraphRecord
from ._schemas import ContractSchemas


def validate_graph_input(graph: GraphRecord, value: JsonObject, schemas: ContractSchemas) -> None:
    if graph.input_schema is not None:
        schemas.validate(value, encode_json(graph.input_schema))
    for identity in graph.components:
        seen: set[str] = set()
        parent: str | None = identity
        while parent is not None:
            if parent in seen or parent not in graph.components:
                raise ValueError("Containment must reference existing parents without cycles")
            seen.add(parent)
            parent = graph.components[parent].contained_by
