"""Immutable trusted bindings for invocation-scoped platform MCP clients."""

import math
from dataclasses import dataclass
from urllib.parse import urlsplit

from ._json import JsonObject, json_object


@dataclass(frozen=True)
class McpResource:
    slot: str
    operation: str
    alias: str


@dataclass(frozen=True)
class McpEndpoint:
    url: str
    timeout_seconds: float
    close_seconds: float
    resources: tuple[McpResource, ...] = ()

    def __post_init__(self) -> None:
        url = urlsplit(self.url)
        if url.scheme != "http" or url.hostname not in {"127.0.0.1", "::1"}:
            raise ValueError("MCP requires an explicit local platform endpoint")
        if (
            not url.port
            or url.username
            or url.password
            or url.query
            or url.fragment
            or url.path != "/mcp"
        ):
            raise ValueError("Invalid platform MCP endpoint")
        for seconds in (self.timeout_seconds, self.close_seconds):
            if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError("MCP timeouts must be finite and positive")
        keys = {(item.slot, item.operation) for item in self.resources}
        if len(keys) != len(self.resources):
            raise ValueError("Duplicate MCP resource binding")
        if any(not item.slot or not item.operation or not item.alias for item in self.resources):
            raise ValueError("MCP resource bindings must be nonempty")
        if any(item.alias == "platform.report" for item in self.resources):
            raise ValueError("The platform report alias cannot be a resource binding")

    def alias(self, slot: str, operation: str) -> str:
        for resource in self.resources:
            if (resource.slot, resource.operation) == (slot, operation):
                return resource.alias
        raise ValueError(f"Missing MCP resource operation: {slot}.{operation}")


def mcp_endpoint_from_record(record: JsonObject) -> McpEndpoint:
    if set(record) != {"url", "timeout_seconds", "close_seconds", "resources"}:
        raise ValueError("Unsupported platform MCP client fields")
    url, timeout, close = record["url"], record["timeout_seconds"], record["close_seconds"]
    if not isinstance(url, str):
        raise ValueError("Invalid platform MCP URL")
    if not isinstance(timeout, int | float) or not isinstance(close, int | float):
        raise ValueError("Invalid platform MCP timeouts")
    resources: list[McpResource] = []
    for slot, value in json_object(record["resources"]).items():
        operations = json_object(value)
        if not operations:
            raise ValueError("MCP resource slots require operations")
        for operation, alias in operations.items():
            if not isinstance(alias, str):
                raise ValueError("Invalid platform MCP alias")
            resources.append(McpResource(slot, operation, alias))
    return McpEndpoint(url, timeout, close, tuple(resources))
