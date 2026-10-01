"""Pinned MCP handlers expose exact schemas only for the authenticated invocation."""

from mcp import types
from mcp.server import Server, ServerRequestContext

from slow_thinker_ii.application import GatewayTool, ManagedGatewayService
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

PROTOCOL = "2026-07-28"


def report_tool() -> types.Tool:
    return types.Tool(
        name="platform.report",
        input_schema={
            "type": "object",
            "properties": {
                "kind": {"enum": ["progress", "state", "explanation", "reasoning"]},
                "schema_version": {"const": "1"},
                "value": {},
                "source_occurred_at": {"type": "number"},
            },
            "required": ["kind", "schema_version", "value"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {"recorded": {"const": True}},
            "required": ["recorded"],
            "additionalProperties": False,
        },
    )


def tool(item: GatewayTool) -> types.Tool:
    return types.Tool(
        name=item.alias,
        input_schema=json_object(decode_json(item.contract.input_schema_json)),
        output_schema=json_object(decode_json(item.contract.output_schema_json)),
    )


class GatewayHandlers:
    def __init__(self, service: ManagedGatewayService, grant: str) -> None:
        self._service, self._grant = service, grant

    def require(self, context: ServerRequestContext[object]) -> None:
        self._service.deadline(self._grant)
        if context.protocol_version != PROTOCOL:
            self._service.reject(self._grant, context.method, "unsupported_protocol")
            raise ValueError("Unsupported managed MCP protocol")

    async def discover(
        self, context: ServerRequestContext[object], params: types.RequestParams
    ) -> types.DiscoverResult:
        del params
        self.require(context)
        return types.DiscoverResult(
            supported_versions=[PROTOCOL],
            cache_scope="private",
            capabilities=types.ServerCapabilities(tools=types.ToolsCapability()),
        )

    async def list_tools(
        self, context: ServerRequestContext[object], params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        self.require(context)
        if params is not None and params.cursor is not None:
            raise ValueError("Unknown managed tool cursor")
        return types.ListToolsResult(
            tools=[*(tool(item) for item in self._service.tools(self._grant)), report_tool()]
        )

    async def call_tool(
        self, context: ServerRequestContext[object], params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        self.require(context)
        arguments = encode_json(json_object(params.arguments or {}))
        value: JsonObject
        if params.name == "platform.report":
            self._service.report(self._grant, arguments)
            value = {"recorded": True}
            is_error = False
        else:
            result = await self._service.invoke(self._grant, params.name, arguments)
            value, is_error = (
                json_object(decode_json(result.result.payload_json)),
                result.result.is_error,
            )
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=encode_json(value))],
            structured_content=value,
            is_error=is_error,
        )


def gateway_server(service: ManagedGatewayService, grant: str) -> Server[object]:
    handlers = GatewayHandlers(service, grant)
    server = Server[object](
        "Slow Thinker II",
        version="0.1.0",
        on_list_tools=handlers.list_tools,
        on_call_tool=handlers.call_tool,
    )
    server.add_request_handler("server/discover", types.RequestParams, handlers.discover)
    return server
