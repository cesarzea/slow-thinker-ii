"""Check component, operation, permission and resource references before planning work."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import OperationContract
from slow_thinker_ii.definitions import ResolvedInstance, ResourceRequirement

from ._models import GraphRecord
from ._schemas import ContractSchemas


def resolved_instances(
    graph: GraphRecord, instances: tuple[ResolvedInstance, ...], schemas: ContractSchemas
) -> dict[str, ResolvedInstance]:
    resolved = {item.instance_id: item for item in instances}
    if len(resolved) != len(instances) or set(resolved) != set(graph.components):
        raise ValueError("Resolve exactly one contract for every configured instance")
    for identity, spec in graph.components.items():
        instance = resolved[identity]
        if (instance.type_id, instance.type_version) != (spec.type_id, spec.type_version):
            raise ValueError("Resolved type does not match its pinned graph reference")
        schemas.validate(spec.config, instance.config_schema_json)
        names = [item.name for item in instance.operations]
        if not names or len(set(names)) != len(names):
            raise ValueError("Declare unique operations for every instance")
    return resolved


def operation(
    instances: Mapping[str, ResolvedInstance], component: str, name: str
) -> OperationContract:
    if component not in instances:
        raise ValueError("Unknown configured component")
    for contract in instances[component].operations:
        if contract.name == name:
            return contract
    raise ValueError("Unknown configured operation")


def permissions(
    graph: GraphRecord, instances: Mapping[str, ResolvedInstance]
) -> set[tuple[str, str, str]]:
    allowed: set[tuple[str, str, str]] = set()
    for rule in graph.permissions:
        if rule.caller not in instances:
            raise ValueError("Unknown permission caller")
        for name in rule.operations:
            operation(instances, rule.target, name)
            key = (rule.caller, rule.target, name)
            if key in allowed:
                raise ValueError("Repeated effective permission")
            allowed.add(key)
    return allowed


def resources(graph: GraphRecord, instances: Mapping[str, ResolvedInstance]) -> None:
    allowed = permissions(graph, instances)
    for identity, spec in graph.components.items():
        declared = {item.slot: item for item in instances[identity].resources}
        if len(declared) != len(instances[identity].resources) or not set(spec.resources) <= set(
            declared
        ):
            raise ValueError("Resource slots must be declared uniquely")
        for name, requirement in declared.items():
            require_resource(identity, spec.resources.get(name), requirement, instances, allowed)


def require_resource(
    identity: str,
    target: str | None,
    requirement: ResourceRequirement,
    instances: Mapping[str, ResolvedInstance],
    allowed: set[tuple[str, str, str]],
) -> None:
    if target is None:
        if requirement.required:
            raise ValueError("Missing required resource binding")
        return
    if target not in instances or requirement.role not in instances[target].roles:
        raise ValueError("Resource binding has an unknown target or incompatible role")
    if any((identity, target, name) not in allowed for name in requirement.operations):
        raise ValueError("A resource binding requires explicit invocation permission")
