"""Resource-aware agent compositions retain exact schemas and explicit permissions."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import decode_json
from slow_thinker_ii.definitions import ResolvedInstance, pointer_tokens

from ._models import ComponentRecord, GraphRecord
from ._sequence_references import operation


def validate_contextual(
    graph: GraphRecord,
    instances: Mapping[str, ResolvedInstance],
    allowed: set[tuple[str, str, str]],
) -> None:
    for identity, component in graph.components.items():
        if component.type_id == "contextual-call":
            _worker(identity, component, instances, allowed)
            _resources(identity, component, instances, allowed)


def _worker(
    identity: str,
    component: ComponentRecord,
    instances: Mapping[str, ResolvedInstance],
    allowed: set[tuple[str, str, str]],
) -> None:
    config = component.config
    target, name = component.resources.get("worker"), config.get("worker_operation")
    if target is None or not isinstance(name, str):
        raise ValueError("ContextualCall requires a worker operation and binding")
    worker = operation(instances, target, name)
    if (identity, target, name) not in allowed:
        raise ValueError("ContextualCall worker requires explicit permission")
    if (
        decode_json(worker.input_schema_json) != config["input_schema"]
        or decode_json(worker.output_schema_json) != config["worker_output_schema"]
    ):
        raise ValueError("ContextualCall and worker schemas must agree")


def _resources(
    identity: str,
    component: ComponentRecord,
    instances: Mapping[str, ResolvedInstance],
    allowed: set[tuple[str, str, str]],
) -> None:
    config = component.config
    if config.get("calculation_enabled", False):
        _required(identity, component, "calculator", "calculate", instances, allowed)
        pointer_tokens(str(config["expression_pointer"]))
    if config.get("memory_read", False):
        _required(identity, component, "memory", "get", instances, allowed)
    if config.get("memory_write", False):
        _required(identity, component, "memory", "put", instances, allowed)
        pointer_tokens(str(config["result_pointer"]))


def _required(
    identity: str,
    component: ComponentRecord,
    slot: str,
    name: str,
    instances: Mapping[str, ResolvedInstance],
    allowed: set[tuple[str, str, str]],
) -> None:
    target = component.resources.get(slot)
    if target is None or (identity, target, name) not in allowed:
        raise ValueError("Enabled context stages require bound resources and explicit permission")
    operation(instances, target, name)
