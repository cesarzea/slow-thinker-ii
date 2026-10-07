"""A local fake platform serving the `platform.report` MCP tool and Chat Completions."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from mcp import types
from mcp.server import Server, ServerRequestContext
from slow_thinker_host import JsonObject, encode_json, json_object
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route


class FakePlatform:
    """Records what hosts send; `reject_reports` makes the report tool fail."""

    def __init__(self) -> None:
        self.base = ""
        self.reports: list[tuple[JsonObject, str]] = []
        self.chats: list[tuple[JsonObject, str]] = []
        self.reject_reports = False

    @property
    def mcp_url(self) -> str:
        return f"{self.base}/mcp"

    @property
    def llm_base_url(self) -> str:
        return f"{self.base}/v1"

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
        value: JsonObject = {"recorded": not self.reject_reports}
        text = types.TextContent(type="text", text=encode_json(value))
        return types.CallToolResult(content=[text], is_error=self.reject_reports)

    async def completions(self, request: Request) -> Response:
        body = json_object(await request.json())
        self.chats.append((body, request.headers.get("authorization", "")))
        return JSONResponse(
            {
                "id": "chatcmpl-1",
                "object": "chat.completion",
                "created": 1,
                "model": body["model"],
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "A reply."},
                    }
                ],
            }
        )


@asynccontextmanager
async def fake_platform() -> AsyncGenerator[FakePlatform]:
    """Serve a fresh fake platform on a free loopback port for the duration of a test."""
    platform = FakePlatform()
    server = Server[object](
        "platform", on_list_tools=platform.list_tools, on_call_tool=platform.call_tool
    )
    chat = Route("/v1/chat/completions", platform.completions, methods=["POST"])
    app = server.streamable_http_app(
        stateless_http=True, json_response=True, custom_starlette_routes=[chat]
    )
    config = uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning", ws="none")
    runner = uvicorn.Server(config)
    serving = asyncio.create_task(runner.serve())
    while not runner.started:
        if serving.done() or runner.should_exit:
            raise RuntimeError("The fake platform stopped before it started")
        await asyncio.sleep(0.005)
    port = runner.servers[0].sockets[0].getsockname()[1]
    platform.base = f"http://127.0.0.1:{port}"
    try:
        yield platform
    finally:
        runner.should_exit = True
        await asyncio.wait_for(serving, timeout=10)
