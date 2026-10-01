"""Optional reported evidence, separate from component execution and model billing."""

import math

from ._contracts import Invocation
from ._json import JsonObject, json_object
from ._mcp_client import managed_mcp_client
from ._mcp_endpoint import McpEndpoint


def _validated_report(report: JsonObject) -> JsonObject:
    value = json_object(report)
    if not {"kind", "schema_version", "value"} <= set(value) or set(value) - {
        "kind",
        "schema_version",
        "value",
        "source_occurred_at",
    }:
        raise ValueError("Unsupported component report fields")
    if value["kind"] not in ("progress", "state", "explanation", "reasoning"):
        raise ValueError("Unsupported component report kind")
    if value["schema_version"] != "1":
        raise ValueError("Unsupported component report schema version")
    if "source_occurred_at" in value:
        timestamp = value["source_occurred_at"]
        if (
            isinstance(timestamp, bool)
            or not isinstance(timestamp, int | float)
            or not math.isfinite(timestamp)
        ):
            raise ValueError("Report source timestamp must be finite")
    return value


async def report_component(
    endpoint: McpEndpoint, invocation: Invocation, report: JsonObject
) -> JsonObject:
    arguments = _validated_report(report)
    async with managed_mcp_client(endpoint, invocation) as client:
        reply = await client.call_tool("platform.report", arguments)
    if reply.is_error:
        raise ValueError("Component report was rejected")
    result = json_object(reply.structured_content)
    if set(result) != {"recorded"} or result["recorded"] is not True:
        raise ValueError("Platform did not confirm durable component reporting")
    return result
