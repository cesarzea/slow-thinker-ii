"""A local fake platform: Chat Completions and the `platform.report` MCP tool over HTTP."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from llm_call_fakes import completion
from mcp import types
from mcp.server import Server, ServerRequestContext
from slow_thinker_host import JsonObject, JsonValue, encode_json, json_object
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


class FakePlatform:
    """Answers model calls with `reply` and records requests and reports with their grant."""

    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.base = ""
        self.chats: list[tuple[JsonObject, str]] = []
        self.reports: list[tuple[JsonValue, str]] = []

    async def list_tools(
        self, context: ServerRequestContext[object], params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        del context, params
        tool = types.Tool(name="platform.report", input_schema={"type": "object"})
        return types.ListToolsResult(tools=[tool])

    async def call_tool(
        self, context: ServerRequestContext[object], params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        authorization = str(context.request.headers["authorization"]) if context.request else ""
        self.reports.append((json_object(params.arguments or {}), authorization))
        text = types.TextContent(type="text", text=encode_json({"recorded": True}))
        return types.CallToolResult(content=[text])

    async def completions(self, request: Request) -> Response:
        self.chats.append((json_object(await request.json()), request.headers["authorization"]))
        return JSONResponse(completion(self.reply))


@asynccontextmanager
async def fake_platform(reply: str) -> AsyncGenerator[FakePlatform]:
    """Serve the fake platform on a free loopback port for the duration of a test."""
    platform = FakePlatform(reply)
    server = Server[object](
        "platform", on_list_tools=platform.list_tools, on_call_tool=platform.call_tool
    )
    chat = Route("/v1/chat/completions", platform.completions, methods=["POST"])
    app = server.streamable_http_app(
        stateless_http=True, json_response=True, custom_starlette_routes=[chat]
    )
    runner = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning", ws="none")
    )
    serving = asyncio.create_task(runner.serve())
    while not runner.started:
        if serving.done() or runner.should_exit:
            raise RuntimeError("The fake platform stopped before it started")
        await asyncio.sleep(0.005)
    platform.base = f"http://127.0.0.1:{runner.servers[0].sockets[0].getsockname()[1]}"
    try:
        yield platform
    finally:
        runner.should_exit = True
        await asyncio.wait_for(serving, timeout=10)
