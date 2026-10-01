"""Validate RoutedCall resources against the exact installed worker and router contracts."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import decode_json, json_object
from slow_thinker_ii.definitions import ResolvedInstance, pointer_tokens

from ._models import GraphRecord
from ._sequence_references import operation, permissions


def validate_compositions(graph: GraphRecord, instances: Mapping[str, ResolvedInstance]) -> None:
    allowed = permissions(graph, instances)
    for identity, component in graph.components.items():
        if component.type_id != "routed-call":
            continue
        config = component.config
        worker_id, router_id = component.resources.get("worker"), component.resources.get("router")
        worker_name = config.get("worker_operation")
        if worker_id is None or router_id is None or not isinstance(worker_name, str):
            raise ValueError("RoutedCall requires worker and router resource bindings")
        worker = operation(instances, worker_id, worker_name)
        router = operation(instances, router_id, "route")
        if (identity, worker_id, worker_name) not in allowed or (
            identity,
            router_id,
            "route",
        ) not in allowed:
            raise ValueError(
                "RoutedCall resources require explicit effective operation permissions"
            )
        if decode_json(worker.input_schema_json) != config["input_schema"]:
            raise ValueError("RoutedCall input schema differs from its installed worker")
        if decode_json(worker.output_schema_json) != config["worker_output_schema"]:
            raise ValueError("RoutedCall output schema differs from its installed worker")
        pointer_tokens(str(config["router_input_pointer"]))
        ports = json_object(json_object(decode_json(router.output_schema_json))["properties"])[
            "port"
        ]
        if json_object(ports).get("enum") != config["outputs"]:
            raise ValueError("RoutedCall outputs differ from its installed router")
