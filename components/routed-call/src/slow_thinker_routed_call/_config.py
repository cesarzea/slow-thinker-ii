"""Freeze schemas and declared resource operations before hosting a composition."""

import re

from slow_thinker_host import JsonObject, JsonValue, check_schema, encode_json, json_object

from ._types import RoutedCallConfig


def parse_config(value: JsonObject) -> RoutedCallConfig:
    if set(value) != {
        "input_schema",
        "worker_operation",
        "worker_output_schema",
        "router_input_pointer",
        "outputs",
    }:
        raise ValueError("Unsupported RoutedCall configuration fields")
    operation, pointer, outputs = (
        value["worker_operation"],
        value["router_input_pointer"],
        value["outputs"],
    )
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("Worker operation must be nonempty")
    if not isinstance(pointer, str) or not re.fullmatch(r"(?:/(?:[^~/]|~[01])*)*", pointer):
        raise ValueError("Router input must be a JSON Pointer")
    ports = _ports(outputs)
    request, reply = json_object(value["input_schema"]), json_object(value["worker_output_schema"])
    if request.get("type") != "object" or reply.get("type") != "object":
        raise ValueError("RoutedCall worker input and output require object schemas")
    check_schema(request)
    check_schema(reply)
    return RoutedCallConfig(encode_json(request), operation, encode_json(reply), pointer, ports)


def _ports(outputs: JsonValue) -> tuple[str, ...]:
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("RoutedCall requires declared outputs")
    if not all(isinstance(port, str) and port.strip() for port in outputs):
        raise ValueError("RoutedCall outputs must be nonempty strings")
    ports = tuple(str(port) for port in outputs)
    if len(set(ports)) != len(ports):
        raise ValueError("RoutedCall outputs must be unique")
    return ports
