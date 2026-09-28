"""Deadline metadata rejects expired work before component invocation."""

import time

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    DEADLINE_META,
    GRANT_META,
    PROTOCOL_VERSION,
    Invocation,
    JsonObject,
    Operation,
    ToolReply,
    create_server,
)


class Receiver:
    def __init__(self) -> None:
        self.received: list[Invocation] = []

    def operations(self) -> tuple[Operation, ...]:
        return (Operation("receive", {"type": "object"}, {"type": "object"}),)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del name, arguments
        self.received.append(context)
        return ToolReply({})


@pytest.mark.parametrize("deadline", [True, "tomorrow", 0, -1])
async def test_invalid_deadline_never_reaches_component(deadline: str | int | bool) -> None:
    receiver = Receiver()
    async with Client(create_server(receiver, "receiver", "1"), mode=PROTOCOL_VERSION) as client:
        with pytest.raises(MCPError):
            await client.call_tool(
                "receive", {}, meta={GRANT_META: "grant", DEADLINE_META: deadline}
            )
    assert not receiver.received


async def test_valid_deadline_is_carried_without_renewal() -> None:
    receiver = Receiver()
    deadline = time.monotonic() + 10
    async with Client(create_server(receiver, "receiver", "1"), mode=PROTOCOL_VERSION) as client:
        await client.call_tool("receive", {}, meta={GRANT_META: "grant", DEADLINE_META: deadline})
    assert receiver.received == [Invocation("grant", deadline)]
