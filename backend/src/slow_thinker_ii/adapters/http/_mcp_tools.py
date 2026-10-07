"""The `platform.report` tool, served for the one grant that authenticated the request."""

from mcp import types
from mcp.server import Server, ServerRequestContext

from slow_thinker_ii.application import InvalidGrant, InvalidReport, ReportService
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json, json_object

REPORT_TOOL = "platform.report"
KINDS: tuple[JsonValue, ...] = ("step", "progress", "state", "explanation", "reasoning")


def report_tool() -> types.Tool:
    return types.Tool(
        name=REPORT_TOOL,
        description="Records a report about the current activation as reported evidence.",
        input_schema={
            "type": "object",
            "properties": {"kind": {"enum": list(KINDS)}, "content": {}},
            "required": ["kind", "content"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {"recorded": {"const": True}},
            "required": ["recorded"],
            "additionalProperties": False,
        },
    )


class ReportHandlers:
    def __init__(self, reports: ReportService, grant: str) -> None:
        self._reports = reports
        self._grant = grant

    async def list_tools(
        self, context: ServerRequestContext[object], params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        del context, params
        return types.ListToolsResult(tools=[report_tool()])

    async def call_tool(
        self, context: ServerRequestContext[object], params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        """Refusals are tool errors with the text `{"code", "message"}`."""
        del context
        if params.name != REPORT_TOOL:
            return failure("unknown_tool", f"The platform offers only the {REPORT_TOOL} tool.")
        try:
            arguments = json_object(params.arguments or {})
        except ValueError:
            arguments = {}
        kind = arguments.get("kind")
        if set(arguments) != {"kind", "content"} or not isinstance(kind, str):
            return failure("invalid_arguments", "A report has exactly a kind and a JSON content.")
        return self._report(kind, arguments["content"])

    def _report(self, kind: str, content: JsonValue) -> types.CallToolResult:
        try:
            self._reports.report(self._grant, kind, content)
        except InvalidGrant as error:  # the call ended after the request was admitted
            return failure("invalid_grant", str(error))
        except InvalidReport as error:
            return failure("invalid_report", str(error))
        recorded: JsonObject = {"recorded": True}
        text = types.TextContent(type="text", text=encode_json(recorded))
        return types.CallToolResult(content=[text], structured_content=recorded)


def failure(code: str, message: str) -> types.CallToolResult:
    text = types.TextContent(type="text", text=encode_json({"code": code, "message": message}))
    return types.CallToolResult(content=[text], is_error=True)


def report_server(reports: ReportService, grant: str) -> Server[object]:
    handlers = ReportHandlers(reports, grant)
    return Server[object](
        "Slow Thinker II",
        version="0.1.0",
        on_list_tools=handlers.list_tools,
        on_call_tool=handlers.call_tool,
    )
