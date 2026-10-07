"""A memory host serves recall and remember, and needs a memory handler."""

import pytest
from host_fixtures import Recorder, bootstrap, connect, error_of, meta
from slow_thinker_host import (
    Context,
    JsonObject,
    JsonValue,
    create_server,
    position_tools,
    tool_schemas,
)

CLOSED: JsonObject = {
    "type": "object",
    "properties": {"message": {}},
    "required": ["message"],
    "additionalProperties": False,
}


class Remembering:
    """A memory handler: recall prefixes what it was told to remember."""

    def __init__(self) -> None:
        self.kept: list[tuple[JsonValue, JsonValue]] = []

    async def recall(self, message: JsonValue, context: Context) -> JsonValue:
        del context
        return {"history": [list(item) for item in self.kept], "message": message}

    async def remember(self, received: JsonValue, replied: JsonValue, context: Context) -> None:
        del context
        self.kept.append((received, replied))


def test_a_memory_exposes_recall_and_remember() -> None:
    (recall, remember) = position_tools("memory")
    assert recall == (
        "recall",
        CLOSED,
        CLOSED,
    )
    assert remember == (
        "remember",
        {
            **CLOSED,
            "properties": {"received": {}, "replied": {}},
            "required": ["received", "replied"],
        },
        {**CLOSED, "properties": {}, "required": []},
    )
    assert tool_schemas("memory") == recall


async def test_a_memory_host_recalls_and_remembers() -> None:
    memory = Remembering()
    async with connect(create_server(bootstrap("memory"), memory=memory)) as client:
        listed = await client.list_tools()
        first = await client.call_tool("recall", {"message": "Hi"}, meta=meta())
        kept = await client.call_tool(
            "remember", {"received": "Hi", "replied": "Hello"}, meta=meta()
        )
        second = await client.call_tool("recall", {"message": "Again"}, meta=meta())
        wrong = await client.call_tool("activate", {"message": "Hi"}, meta=meta())
    assert [tool.name for tool in listed.tools] == ["recall", "remember"]
    assert first.structured_content == {"message": {"history": [], "message": "Hi"}}
    assert kept.structured_content == {}
    assert second.structured_content == {
        "message": {"history": [["Hi", "Hello"]], "message": "Again"}
    }
    assert error_of(wrong) == {
        "code": "unknown_tool",
        "message": "This host serves only recall, remember.",
    }


def test_a_memory_host_requires_a_memory_handler() -> None:
    with pytest.raises(ValueError, match="requires a memory handler"):
        create_server(bootstrap("memory"), node=Recorder())
