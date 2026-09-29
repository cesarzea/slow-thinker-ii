"""Definition projections preserve configured identities and relationship categories."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object


def graph_input_schema(definition: JsonObject) -> JsonObject:
    declared = definition.get("input_schema")
    if declared is not None:
        return json_object(declared)
    return {
        "type": "object",
        "properties": {"problem": {"type": "string"}},
        "required": ["problem"],
        "additionalProperties": False,
    }


def graph_detail(definition: JsonObject, roles: Mapping[str, tuple[str, ...]]) -> JsonObject:
    components = json_object(definition["components"])
    nodes = json_object(definition["nodes"])
    entries: list[JsonValue] = []
    for identity, value in components.items():
        component = json_object(value)
        entries.append(
            {
                "id": identity,
                "type_id": component["type_id"],
                "type_version": component["type_version"],
                "roles": list(roles.get(identity, ())),
                "contained_by": component.get("contained_by"),
            }
        )
    planned: list[JsonValue] = [
        {"id": identity, "component": json_object(value)["component"]}
        for identity, value in nodes.items()
    ]
    return {
        "graph_id": definition["graph_id"],
        "revision": definition["revision"],
        "input_schema": graph_input_schema(definition),
        "definition": definition,
        "structure": {"components": entries, "nodes": planned, "edges": relationships(definition)},
    }


def relationships(definition: JsonObject) -> list[JsonValue]:
    components = json_object(definition["components"])
    edges = control_edges(definition)
    rules = definition["permissions"]
    if not isinstance(rules, list):
        raise ValueError("Permissions must be a list")
    for value in rules:
        rule = json_object(value)
        operations = rule["operations"]
        if not isinstance(operations, list):
            raise ValueError("Permission operations must be a list")
        edges.extend(
            {
                "id": f"permission:{rule['caller']}:{rule['target']}:{name}",
                "kind": "permission",
                "source": rule["caller"],
                "target": rule["target"],
                "label": name,
            }
            for name in operations
        )
    return edges + binding_edges(components)


def binding_edges(components: JsonObject) -> list[JsonValue]:
    edges: list[JsonValue] = []
    for identity, value in components.items():
        for slot, target in json_object(json_object(value)["resources"]).items():
            edges.append(
                {
                    "id": f"binding:{identity}:{slot}",
                    "kind": "binding",
                    "source": identity,
                    "target": target,
                    "label": slot,
                }
            )
    return edges


def control_edges(definition: JsonObject) -> list[JsonValue]:
    controller = json_object(definition["controller"])
    component = json_object(json_object(definition["components"])[str(controller["component"])])
    config = json_object(component["config"])
    edges: list[JsonValue] = []
    if definition.get("execution_profile") == "bounded-conditional":
        for node, routes in json_object(config["routes"]).items():
            edges.extend(
                {
                    "id": f"control:{node}:{port}",
                    "kind": "control",
                    "source": node,
                    "target": target,
                    "label": port,
                }
                for port, target in json_object(routes).items()
            )
    else:
        steps = config["steps"]
        if not isinstance(steps, list):
            raise ValueError("Sequence steps must be a list")
        return sequence_edges(steps)
    return edges


def sequence_edges(steps: list[JsonValue]) -> list[JsonValue]:
    edges: list[JsonValue] = []
    for index, node in enumerate(steps):
        edges.append(
            {
                "id": f"control:{node}:next",
                "kind": "control",
                "source": node,
                "target": steps[index + 1] if index + 1 < len(steps) else None,
                "label": "next",
            }
        )
    return edges
