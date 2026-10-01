"""Validate and freeze deterministic selector configuration at trusted setup."""

import re
from collections.abc import Callable
from importlib import import_module
from inspect import isasyncgenfunction, iscoroutinefunction, signature
from typing import cast

from slow_thinker_host import JsonObject, JsonValue, check_schema, encode_json, json_object

from ._types import RedirectorConfig


def parse_config(value: JsonObject) -> RedirectorConfig:
    if set(value) != {"outputs", "selector", "input_schema"}:
        raise ValueError("Unsupported Redirector configuration fields")
    outputs = value["outputs"]
    if not isinstance(outputs, list) or not outputs:
        raise ValueError("Redirector requires declared outputs")
    if not all(isinstance(port, str) and port.strip() for port in outputs):
        raise ValueError("Redirector outputs must be nonempty strings")
    ports = tuple(str(port) for port in outputs)
    if len(set(ports)) != len(ports):
        raise ValueError("Redirector outputs must be unique")
    selector = value["selector"]
    if not isinstance(selector, str) or not re.fullmatch(
        r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*", selector
    ):
        raise ValueError("Selector must be an installed module:callable reference")
    schema = json_object(value["input_schema"])
    check_schema(schema)
    return RedirectorConfig(ports, selector, encode_json(schema))


def load_selector(reference: str) -> Callable[[JsonValue], str]:
    """Resolve packaged trusted code without invoking it or accepting invocation paths."""
    module, name = reference.split(":")
    selected: object = getattr(import_module(module), name)
    if not callable(selected):
        raise ValueError("Configured selector is not callable")
    implementation = type(selected).__call__
    if any(
        iscoroutinefunction(candidate) or isasyncgenfunction(candidate)
        for candidate in (selected, implementation)
    ):
        raise ValueError("Configured selector must be synchronous")
    signature(selected).bind(None)
    return cast(Callable[[JsonValue], str], selected)
