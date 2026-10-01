"""Deterministic HTTP gateway fixture using the ordinary pinned MCP client wire."""

import asyncio
from types import TracebackType

import httpx2
import pytest
from slow_thinker_host import (
    JsonObject,
    Operation,
    ToolReply,
    decode_json,
    encode_json,
    json_object,
)

_CLIENT = httpx2.AsyncClient


class ClosingClient(_CLIENT):
    close_wait: asyncio.Event | None = None

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: TracebackType | None = None,
    ) -> None:
        await super().__aexit__(exc_type, exc_value, traceback)
        if self.close_wait is not None:
            await self.close_wait.wait()


class GatewayFixture:
    def __init__(self) -> None:
        self.operations: dict[str, Operation] = {}
        self.replies: dict[str, ToolReply] = {}
        self.calls: list[tuple[str, JsonObject, str]] = []
        self.requests: list[httpx2.Request] = []
        self.clients: list[httpx2.AsyncClient] = []
        self.versions = ["2026-07-28"]
        self.capabilities: JsonObject = {"tools": {}}
        self.status = 200
        self.cursor: str | None = None
        self.block = False
        self.block_close = False
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    def add(self, alias: str, reply: ToolReply, schema: JsonObject | None = None) -> None:
        self.operations[alias] = Operation(alias, schema or {"type": "object"}, {"type": "object"})
        self.replies[alias] = reply

    def install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def client(
            *, headers: dict[str, str], timeout: float, trust_env: bool, follow_redirects: bool
        ) -> httpx2.AsyncClient:
            assert not trust_env and not follow_redirects
            instance = ClosingClient(
                headers=headers,
                timeout=timeout,
                trust_env=False,
                follow_redirects=False,
                transport=httpx2.MockTransport(self.handle),
            )
            if self.block_close:
                instance.close_wait = asyncio.Event()
            self.clients.append(instance)
            return instance

        monkeypatch.setattr("slow_thinker_host._mcp_client.httpx2.AsyncClient", client)

    async def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        if request.method != "POST":
            return httpx2.Response(405)
        if self.status != 200:
            return httpx2.Response(self.status)
        record = json_object(decode_json(request.content.decode()))
        method = record.get("method")
        if method == "server/discover":
            result = json_object(
                {
                    "supportedVersions": self.versions,
                    "capabilities": self.capabilities,
                    "ttlMs": 0,
                    "cacheScope": "private",
                    "resultType": "complete",
                }
            )
        elif method == "tools/list":
            result = self.listed()
        else:
            assert method == "tools/call"
            result = await self.called(json_object(record["params"]), request)
        return httpx2.Response(200, json={"jsonrpc": "2.0", "id": record["id"], "result": result})

    def listed(self) -> JsonObject:
        result: JsonObject = {
            "ttlMs": 0,
            "cacheScope": "private",
            "resultType": "complete",
            "tools": [
                {"name": op.name, "inputSchema": op.input_schema, "outputSchema": op.output_schema}
                for op in self.operations.values()
            ],
        }
        if self.cursor is not None:
            result["nextCursor"] = self.cursor
        return result

    async def called(self, params: JsonObject, request: httpx2.Request) -> JsonObject:
        alias = str(params["name"])
        arguments = json_object(params.get("arguments", {}))
        self.calls.append((alias, arguments, request.headers["authorization"]))
        self.started.set()
        if self.block:
            await self.release.wait()
        reply = self.replies[alias]
        return {
            "content": [{"type": "text", "text": encode_json(reply.value)}],
            "resultType": "complete",
            "structuredContent": reply.value,
            "isError": reply.is_error,
        }
