"""Pin the protocol and compare wire discovery with admitted operation contracts."""

from mcp import Client, types
from pydantic import JsonValue, TypeAdapter

from slow_thinker_ii.contracts import OperationContract

PROTOCOL_VERSION = "2026-07-28"
GRANT_META = "slow-thinker-ii/invocation-grant"
DEADLINE_META = "slow-thinker-ii/deadline-monotonic"
JSON_OBJECT = TypeAdapter(dict[str, JsonValue])


async def require_ready(client: Client, operations: tuple[OperationContract, ...]) -> None:
    discovered = await client.session.send_request(types.DiscoverRequest(), types.DiscoverResult)
    if PROTOCOL_VERSION not in discovered.supported_versions:
        raise ValueError("Component does not support the pinned MCP protocol")
    capabilities = discovered.capabilities.model_dump(exclude_none=True, by_alias=True)
    if set(capabilities) != {"tools"}:
        raise ValueError("Component advertises unsupported capabilities")
    listed = await client.list_tools()
    expected = {item.name: item for item in operations}
    if listed.next_cursor is not None or len(listed.tools) != len(expected):
        raise ValueError("Unexpected component operation listing")
    if {item.name for item in listed.tools} != set(expected):
        raise ValueError("Component operation names do not match")
    for tool in listed.tools:
        contract = expected[tool.name]
        if tool.input_schema != JSON_OBJECT.validate_json(contract.input_schema_json):
            raise ValueError("Component input schema does not match")
        if tool.output_schema != JSON_OBJECT.validate_json(contract.output_schema_json):
            raise ValueError("Component output schema does not match")
