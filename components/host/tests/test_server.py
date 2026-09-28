"""Actual SDK requests exercise capabilities, validation, authority and isolation."""

import asyncio

import pytest
from mcp import Client, types
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    GRANT_META,
    PROTOCOL_VERSION,
    Invocation,
    JsonObject,
    Operation,
    ToolReply,
    create_server,
    json_object,
)

SCHEMA: JsonObject = {
    "type": "object",
    "properties": {"value": {"type": "integer"}},
    "required": ["value"],
    "additionalProperties": False,
}


class Echo:
    def __init__(self) -> None:
        self.contexts: list[Invocation] = []
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.release.set()
        self.invalid = False
        self.schema = json_object(SCHEMA)
        self.operation_names: tuple[str, ...] = ("echo",)

    def operations(self) -> tuple[Operation, ...]:
        return tuple(Operation(name, self.schema, self.schema) for name in self.operation_names)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        assert name == "echo"
        self.contexts.append(context)
        self.started.set()
        await self.release.wait()
        return ToolReply({"value": "wrong"} if self.invalid else arguments)


async def test_actual_discovery_and_fresh_invocation_contexts() -> None:
    component = Echo()
    async with Client(create_server(component, "echo", "1"), mode=PROTOCOL_VERSION) as client:
        discovery = await client.session.send_request(types.DiscoverRequest(), types.DiscoverResult)
        assert set(discovery.capabilities.model_dump(exclude_none=True)) == {"tools"}
        assert PROTOCOL_VERSION in discovery.supported_versions
        tools = await client.list_tools()
        assert tools.tools[0].input_schema == SCHEMA
        assert tools.tools[0].output_schema == SCHEMA
        for grant in ("first", "second"):
            result = await client.call_tool("echo", {"value": 7}, meta={GRANT_META: grant})
            assert result.structured_content == {"value": 7}
    assert [context.grant for context in component.contexts] == ["first", "second"]
    assert component.contexts[0] is not component.contexts[1]


async def test_bad_arguments_and_missing_authority_never_reach_component() -> None:
    component = Echo()
    async with Client(create_server(component, "echo", "1"), mode=PROTOCOL_VERSION) as client:
        with pytest.raises(MCPError):
            await client.call_tool("echo", {"value": 7})
        with pytest.raises(MCPError):
            await client.call_tool("echo", {"value": "7"}, meta={GRANT_META: "test"})
        with pytest.raises(MCPError):
            await client.call_tool("absent", {}, meta={GRANT_META: "test"})
    assert not component.contexts


async def test_invalid_output_fails_without_poisoning_next_invocation() -> None:
    component = Echo()
    component.invalid = True
    async with Client(create_server(component, "echo", "1"), mode=PROTOCOL_VERSION) as client:
        with pytest.raises(MCPError):
            await client.call_tool("echo", {"value": 7}, meta={GRANT_META: "test"})
        component.invalid = False
        result = await client.call_tool("echo", {"value": 8}, meta={GRANT_META: "new"})
        assert result.structured_content == {"value": 8}


async def test_busy_host_rejects_another_call_without_queueing() -> None:
    component = Echo()
    component.release.clear()
    async with Client(create_server(component, "echo", "1"), mode=PROTOCOL_VERSION) as client:
        first = asyncio.create_task(client.call_tool("echo", {"value": 1}, meta={GRANT_META: "a"}))
        await asyncio.wait_for(component.started.wait(), timeout=2)
        try:
            with pytest.raises(MCPError):
                await client.call_tool("echo", {"value": 2}, meta={GRANT_META: "b"})
        finally:
            component.release.set()
        assert (await first).structured_content == {"value": 1}
    assert len(component.contexts) == 1


async def test_declared_schema_is_frozen_before_component_can_mutate_it() -> None:
    component = Echo()
    server = create_server(component, "echo", "1")
    component.schema.clear()
    async with Client(server, mode=PROTOCOL_VERSION) as client:
        listed = await client.list_tools()
        assert listed.tools[0].input_schema == SCHEMA
        with pytest.raises(MCPError):
            await client.call_tool("echo", {"value": "wrong"}, meta={GRANT_META: "grant"})
    assert not component.contexts


@pytest.mark.parametrize("names", [(), ("echo", "echo")])
def test_empty_or_duplicate_operation_declarations_are_rejected(names: tuple[str, ...]) -> None:
    component = Echo()
    component.operation_names = names
    with pytest.raises(ValueError, match="uniquely named"):
        create_server(component, "echo", "1")


async def test_host_rejects_legacy_protocol_requests() -> None:
    async with Client(create_server(Echo(), "echo", "1"), mode="legacy") as client:
        with pytest.raises(MCPError, match="Unsupported component protocol"):
            await client.list_tools()
