"""Actual MCP requests exercise tool exposure, both operations and argument checks."""

import pytest
from host_fixtures import Recorder, bootstrap, connect, entries, error_of, meta
from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import JsonObject, Position, create_server, tool_schemas

ACTIVATE_INPUT: JsonObject = {
    "type": "object",
    "properties": {"message": {}},
    "required": ["message"],
    "additionalProperties": False,
}
EMISSION: JsonObject = {
    "type": "object",
    "properties": {"port": {"type": "string"}, "payload": {}},
    "required": ["port", "payload"],
    "additionalProperties": False,
}


@pytest.mark.parametrize("position", ["node", "output"])
async def test_host_exposes_exactly_the_tool_of_its_position(position: Position) -> None:
    server = create_server(bootstrap(position), node=Recorder(), output=Recorder())
    async with connect(server) as client:
        listed = await client.list_tools()
    name, input_schema, output_schema = tool_schemas(position)
    assert [(tool.name, tool.input_schema, tool.output_schema) for tool in listed.tools] == [
        (name, input_schema, output_schema)
    ]


def test_tool_schemas_are_the_protocol_shapes() -> None:
    assert tool_schemas("node") == (
        "activate",
        ACTIVATE_INPUT,
        {
            **ACTIVATE_INPUT,
            "properties": {"emissions": {"type": "array", "items": EMISSION}},
            "required": ["emissions"],
        },
    )
    assert tool_schemas("output") == (
        "select_output",
        {
            **ACTIVATE_INPUT,
            "properties": {"received": {}, "node_input": {}},
            "required": ["received", "node_input"],
        },
        EMISSION,
    )


async def test_activate_returns_the_handler_emissions_with_its_context() -> None:
    handler = Recorder()
    async with connect(create_server(bootstrap("node"), node=handler)) as client:
        result = await client.call_tool("activate", {"message": {"text": "ñ"}}, meta=meta())
    assert result.structured_content == {"emissions": [{"port": "out", "payload": {"text": "ñ"}}]}
    assert not result.is_error and handler.messages == [{"text": "ñ"}]
    assert handler.contexts[0].activation_id == "a1"


async def test_select_output_receives_both_values() -> None:
    handler = Recorder()
    async with connect(create_server(bootstrap("output"), output=handler)) as client:
        result = await client.call_tool(
            "select_output", {"received": [1], "node_input": "story"}, meta=meta()
        )
    assert result.structured_content == {
        "port": "chosen",
        "payload": {"received": [1], "node_input": "story"},
    }


@pytest.mark.parametrize(
    ("name", "arguments", "code"),
    [
        ("select_output", {"received": 1, "node_input": 2}, "unknown_tool"),
        ("activate", {}, "invalid_arguments"),
        ("activate", {"message": 1, "extra": True}, "invalid_arguments"),
    ],
)
async def test_unknown_tools_and_invalid_arguments_never_reach_the_handler(
    name: str, arguments: JsonObject, code: str
) -> None:
    handler = Recorder()
    async with connect(create_server(bootstrap("node"), node=handler)) as client:
        result = await client.call_tool(name, arguments, meta=meta())
    assert error_of(result)["code"] == code and not handler.messages


@pytest.mark.parametrize(
    "record",
    [
        {},
        {"slow-thinker/grant": "", "slow-thinker/budget-ms": 10, "slow-thinker/activation-id": "a"},
        {
            "slow-thinker/grant": "g",
            "slow-thinker/budget-ms": "9",
            "slow-thinker/activation-id": "a",
        },
        {
            "slow-thinker/grant": "g",
            "slow-thinker/budget-ms": True,
            "slow-thinker/activation-id": "a",
        },
        {
            "slow-thinker/grant": "g",
            "slow-thinker/budget-ms": -1,
            "slow-thinker/activation-id": "a",
        },
        {"slow-thinker/grant": "g", "slow-thinker/budget-ms": 10, "slow-thinker/activation-id": 7},
    ],
)
async def test_calls_without_valid_metadata_are_invalid_requests(record: JsonObject) -> None:
    handler = Recorder()
    async with connect(create_server(bootstrap("node"), node=handler)) as client:
        result = await client.call_tool("activate", {"message": 1}, meta=entries(record))
    assert error_of(result)["code"] == "invalid_request" and not handler.messages


@pytest.mark.parametrize("position", ["node", "output"])
def test_the_position_requires_its_handler(position: Position) -> None:
    with pytest.raises(ValueError, match=f"position {position} requires"):
        create_server(bootstrap(position))


async def test_host_rejects_the_legacy_protocol() -> None:
    server = create_server(bootstrap("node"), node=Recorder())
    async with Client(server, mode="legacy") as client:
        with pytest.raises(MCPError, match="Unsupported component protocol"):
            await client.list_tools()
        with pytest.raises(MCPError, match="Unsupported component protocol"):
            await client.call_tool("activate", {"message": 1}, meta=meta())
