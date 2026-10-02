"""Strict resource replies; all calls use the already managed MCP session."""

from collections.abc import Awaitable

from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import JsonObject, JsonValue, McpEndpoint, json_object, validate_value


async def stage[T](name: str, action: Awaitable[T]) -> T:
    try:
        return await action
    except Exception as error:
        raise MCPError(
            code=-32603,
            message="contextual_call_failed",
            data={"stage": name, "reason": str(error)[:160]},
        ) from error


async def call(
    client: Client,
    endpoint: McpEndpoint,
    slot: str,
    operation: str,
    arguments: JsonObject,
) -> JsonObject:
    reply = await client.call_tool(endpoint.alias(slot, operation), arguments)
    if reply.is_error:
        raise ValueError("Bound component returned an error")
    return json_object(reply.structured_content)


async def memory_get(client: Client, endpoint: McpEndpoint, key: str) -> JsonValue:
    reply = await call(client, endpoint, "memory", "get", {"key": key})
    found, version = reply.get("found"), reply.get("version")
    if set(reply) != {"found", "value", "version"} or type(found) is not bool:
        raise ValueError("Memory get response has an invalid shape")
    if found:
        if type(version) is not int or version <= 0:
            raise ValueError("Memory get response has an invalid version")
    elif version is not None or reply["value"] is not None:
        raise ValueError("Missing memory value has an invalid response")
    return reply["value"]


async def calculate(client: Client, endpoint: McpEndpoint, expression: JsonValue) -> str:
    if not isinstance(expression, str):
        raise ValueError("Calculation expression pointer must select a string")
    reply = await call(client, endpoint, "calculator", "calculate", {"expression": expression})
    value = reply.get("value")
    if set(reply) != {"expression", "value"} or reply["expression"] != expression:
        raise ValueError("Calculator response has an invalid identity or shape")
    if not isinstance(value, str) or not value:
        raise ValueError("Calculator response has an invalid value")
    return value


async def worker(
    client: Client,
    endpoint: McpEndpoint,
    operation: str,
    arguments: JsonObject,
    schema: JsonObject,
) -> JsonObject:
    reply = await call(client, endpoint, "worker", operation, arguments)
    validate_value(reply, schema)
    if reply.get("status") == "error":
        raise ValueError("Worker returned an unsuccessful result")
    return reply


async def memory_put(client: Client, endpoint: McpEndpoint, key: str, value: JsonValue) -> None:
    reply = await call(client, endpoint, "memory", "put", {"key": key, "value": value})
    version = reply.get("version")
    if set(reply) != {"version"} or type(version) is not int or version <= 0:
        raise ValueError("Memory put response has an invalid shape")
