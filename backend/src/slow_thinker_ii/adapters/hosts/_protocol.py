"""The platform's side of the component protocol: wire names, tool schemas, bootstraps."""

from typing import Final

from mcp.types import RequestParamsMeta

from slow_thinker_ii.contracts import JsonObject, json_object
from slow_thinker_ii.engine import CallContext, Position
from slow_thinker_ii.graphs import PlanComponent, PlanNode

from ._settings import HostSettings

PROTOCOL_VERSION: Final = "2026-07-28"
GRANT_META: Final = "slow-thinker/grant"
BUDGET_META: Final = "slow-thinker/budget-ms"
ACTIVATION_META: Final = "slow-thinker/activation-id"


def _closed(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _emission() -> JsonObject:
    return _closed({"port": {"type": "string"}, "payload": {}})


type ToolSchema = tuple[str, JsonObject, JsonObject]  # name, input schema, output schema


def protocol_tool(position: Position) -> ToolSchema:
    """The first tool a host at `position` must expose: name, input and output schema."""
    return protocol_tools(position)[0]


def protocol_tools(position: Position) -> tuple[ToolSchema, ...]:
    """Every tool a host at `position` must expose; a memory serves `recall` and `remember`."""
    if position == "node":
        emissions: JsonObject = {"type": "array", "items": _emission()}
        return (("activate", _closed({"message": {}}), _closed({"emissions": emissions})),)
    if position == "memory":
        return (
            ("recall", _closed({"message": {}}), _closed({"message": {}})),
            ("remember", _closed({"received": {}, "replied": {}}), _closed({})),
        )
    return (("select_output", _closed({"received": {}, "node_input": {}}), _emission()),)


def call_meta(context: CallContext) -> RequestParamsMeta:
    """The `_meta` entries of one call: grant, relative budget and activation id."""
    return {
        GRANT_META: context.grant,
        BUDGET_META: context.budget_ms,
        ACTIVATION_META: context.activation_id,
    }


def bootstrap_document(
    node: PlanNode, position: Position, part: PlanComponent, settings: HostSettings
) -> JsonObject:
    """The `slow-thinker.bootstrap/1` document of one host."""
    return {
        "format": "slow-thinker.bootstrap/1",
        "component": str(part.declaration.ref),
        "node": {"id": node.id, "name": node.name},
        "position": position,
        "config": json_object(part.config),
        "platform": {"llm_base_url": settings.llm_base_url, "mcp_url": settings.mcp_url},
        "limits": {"max_concurrent_invocations": settings.max_concurrent_invocations},
    }
