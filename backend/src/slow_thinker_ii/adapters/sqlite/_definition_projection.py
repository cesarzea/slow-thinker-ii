"""Saved graph projections derive only from the admitted immutable snapshot."""

from slow_thinker_ii.contracts import JsonObject, json_object
from slow_thinker_ii.definitions import graph_detail


def saved_definition(snapshot: JsonObject, run: str) -> JsonObject:
    execution = json_object(snapshot.get("execution", {}))
    definition = execution.get("definition")
    result: JsonObject = {"schema_version": "0.1-draft", "run_id": run, "execution": execution}
    if not isinstance(definition, dict):
        return result
    instances = json_object(execution.get("instances", {}))
    roles: dict[str, tuple[str, ...]] = {}
    for identity, value in instances.items():
        descriptor = json_object(json_object(value).get("descriptor", {}))
        declared = descriptor.get("roles", [])
        if not isinstance(declared, list) or any(not isinstance(role, str) for role in declared):
            raise ValueError("Saved roles are malformed")
        roles[identity] = tuple(str(role) for role in declared)
    result.update(graph_detail(definition, roles))
    return result
