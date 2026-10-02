"""Check containment, controller, resources and managed invocation permissions."""

from slow_thinker_ii.contracts import OperationContract
from slow_thinker_ii.definitions import ResolvedInstance

from .._contextual_contracts import validate_contextual
from .._models import ComponentRecord, GraphRecord
from ._diagnostics import pointer, require


def operation(
    instances: dict[str, ResolvedInstance], component: str, name: str, path: str
) -> OperationContract:
    require(component in instances, path, "Component reference must identify a declared instance.")
    contracts = {item.name: item for item in instances[component].operations}
    require(name in contracts, path, "Operation reference must identify a declared operation.")
    return contracts[name]


def containment(graph: GraphRecord) -> None:
    for identity in graph.components:
        seen: set[str] = set()
        parent: str | None = identity
        path = pointer(("components", identity, "contained_by"))
        while parent is not None:
            require(
                parent not in seen and parent in graph.components,
                path,
                "Containment must identify existing parents without cycles.",
            )
            seen.add(parent)
            parent = graph.components[parent].contained_by


def controller(graph: GraphRecord, instances: dict[str, ResolvedInstance]) -> None:
    selected = graph.controller
    operation(instances, selected.component, selected.operation, "/controller")
    require(
        "control" in instances[selected.component].roles,
        "/controller/component",
        "The selected controller must declare the control role.",
    )


def permissions(
    graph: GraphRecord, instances: dict[str, ResolvedInstance]
) -> set[tuple[str, str, str]]:
    allowed: set[tuple[str, str, str]] = set()
    for index, rule in enumerate(graph.permissions):
        path = pointer(("permissions", index))
        require(rule.caller in instances, path, "Permission caller must be a declared instance.")
        for name in rule.operations:
            operation(instances, rule.target, name, path)
            key = rule.caller, rule.target, name
            require(
                key not in allowed, path, "Effective invocation permissions cannot be repeated."
            )
            allowed.add(key)
    return allowed


def resources(
    graph: GraphRecord, instances: dict[str, ResolvedInstance], allowed: set[tuple[str, str, str]]
) -> None:
    for identity, spec in graph.components.items():
        declared = {item.slot: item for item in instances[identity].resources}
        path = pointer(("components", identity, "resources"))
        require(
            set(spec.resources) <= set(declared),
            path,
            "Resource slots must be declared by the type.",
        )
        for slot, requirement in declared.items():
            target = spec.resources.get(slot)
            if target is None:
                require(not requirement.required, path, "A required resource binding is missing.")
                continue
            require(
                target in instances and requirement.role in instances[target].roles,
                path,
                "Resource target must be a declared instance with the required role.",
            )
            require(
                all((identity, target, name) in allowed for name in requirement.operations),
                path,
                "Resource operations require explicit invocation permissions.",
            )


def compositions(
    graph: GraphRecord, instances: dict[str, ResolvedInstance], allowed: set[tuple[str, str, str]]
) -> None:
    validate_contextual(graph, instances, allowed)
    for identity, component in graph.components.items():
        if component.type_id != "routed-call":
            continue
        _routed(identity, component, graph, instances, allowed)


def _routed(
    identity: str,
    component: ComponentRecord,
    graph: GraphRecord,
    instances: dict[str, ResolvedInstance],
    allowed: set[tuple[str, str, str]],
) -> None:
    config, bindings = component.config, component.resources
    path = pointer(("components", identity, "resources"))
    worker_id, router_id = bindings["worker"], bindings["router"]
    worker_name = str(config["worker_operation"])
    operation(instances, worker_id, worker_name, path)
    operation(instances, router_id, "route", path)
    require(
        (identity, worker_id, worker_name) in allowed and (identity, router_id, "route") in allowed,
        path,
        "Composition worker and router operations require explicit permissions.",
    )
    worker_schema = graph.components[worker_id].config.get("input_schema")
    if worker_schema is not None:
        require(
            worker_schema == config["input_schema"],
            path,
            "Composition and worker inputs must agree.",
        )
    ports = graph.components[router_id].config.get("outputs")
    if ports is not None:
        require(ports == config["outputs"], path, "Composition and router output ports must agree.")
