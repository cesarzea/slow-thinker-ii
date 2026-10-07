"""Bootstraps, call metadata and recording handlers for host SDK tests."""

import asyncio
from collections.abc import Sequence
from dataclasses import replace
from typing import cast

from mcp import Client, types
from mcp.server import Server
from mcp.types import RequestParamsMeta
from slow_thinker_host import (
    ACTIVATION_META,
    BUDGET_META,
    GRANT_META,
    PROTOCOL_VERSION,
    Bootstrap,
    Context,
    Emission,
    JsonObject,
    JsonValue,
    Position,
    decode_json,
    json_object,
)

BOOTSTRAP = Bootstrap(
    component="echo@1.0.0",
    node_id="echo",
    node_name="Echo",
    position="node",
    config={},
    llm_base_url="http://127.0.0.1:9/v1",
    mcp_url="http://127.0.0.1:9/mcp",
    max_concurrent_invocations=4,
)


def bootstrap(position: Position = "node", *, concurrency: int = 4) -> Bootstrap:
    return replace(BOOTSTRAP, position=position, max_concurrent_invocations=concurrency)


def meta(budget_ms: float = 2000, grant: str = "grant-1") -> RequestParamsMeta:
    return {GRANT_META: grant, BUDGET_META: budget_ms, ACTIVATION_META: "a1"}


def entries(record: JsonObject) -> RequestParamsMeta:
    """Arbitrary, possibly invalid, `_meta` entries."""
    return cast(RequestParamsMeta, record)


def connect(server: Server[object]) -> Client:
    return Client(server, mode=PROTOCOL_VERSION)


def error_of(result: types.CallToolResult) -> JsonObject:
    """The `{code, message}` of a tool error."""
    assert result.is_error and result.structured_content is None
    content = result.content[0]
    assert isinstance(content, types.TextContent)
    return json_object(decode_json(content.text))


class Recorder:
    """A node and output handler that records calls and can be held or made to fail."""

    def __init__(self) -> None:
        self.contexts: list[Context] = []
        self.messages: list[JsonValue] = []
        self.running = 0
        self.peak = 0
        self.release = asyncio.Event()
        self.release.set()
        self.failure: Exception | None = None

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        await self._enter(message, context)
        return [Emission("out", message)]

    async def select_output(
        self, received: JsonValue, node_input: JsonValue, context: Context
    ) -> Emission:
        await self._enter(received, context)
        return Emission("chosen", {"received": received, "node_input": node_input})

    async def _enter(self, message: JsonValue, context: Context) -> None:
        self.contexts.append(context)
        self.messages.append(message)
        self.running += 1
        self.peak = max(self.peak, self.running)
        try:
            await self.release.wait()
        finally:
            self.running -= 1
        if self.failure is not None:
            raise self.failure
