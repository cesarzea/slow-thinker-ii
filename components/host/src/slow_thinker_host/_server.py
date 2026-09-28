"""Exact tool schemas and invocation isolation over the current MCP protocol."""

import asyncio
import math
import time

from mcp import types
from mcp.server import Server, ServerRequestContext
from mcp.server.stdio import stdio_server

from ._contracts import HostedComponent, Invocation, Operation
from ._json import encode_json, json_object
from ._schemas import check_schema, validate_value

PROTOCOL_VERSION = "2026-07-28"
GRANT_META = "slow-thinker-ii/invocation-grant"
DEADLINE_META = "slow-thinker-ii/deadline-monotonic"


class ComponentServer:
    def __init__(self, component: HostedComponent) -> None:
        self._component = component
        declared = tuple(
            Operation(item.name, json_object(item.input_schema), json_object(item.output_schema))
            for item in component.operations()
        )
        self._operations = {item.name: item for item in declared}
        if not declared or len(declared) != len(self._operations):
            raise ValueError("A component requires uniquely named operations")
        for item in declared:
            check_schema(item.input_schema)
            check_schema(item.output_schema)
        self._busy = False

    async def list_tools(
        self, context: ServerRequestContext[object], params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        del params
        self._check_protocol(context)
        return types.ListToolsResult(tools=[self._tool(item) for item in self._operations.values()])

    async def call_tool(
        self, context: ServerRequestContext[object], params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        self._check_protocol(context)
        if self._busy:
            raise ValueError("Component is already busy")
        operation = self._operations.get(params.name)
        if operation is None:
            raise ValueError("Unknown operation")
        invocation = self._invocation(context)
        arguments = json_object(params.arguments or {})
        validate_value(arguments, operation.input_schema)
        self._busy = True
        try:
            reply = await self._component.invoke(params.name, arguments, invocation)
            validate_value(reply.value, operation.output_schema)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=encode_json(reply.value))],
                structured_content=reply.value,
                is_error=reply.is_error,
            )
        finally:
            self._busy = False

    @staticmethod
    def _invocation(context: ServerRequestContext[object]) -> Invocation:
        grant = (context.meta or {}).get(GRANT_META)
        if not isinstance(grant, str) or not grant:
            raise ValueError("Invocation authority is required")
        deadline: object = (context.meta or {}).get(DEADLINE_META)
        if deadline is not None:
            if isinstance(deadline, bool) or not isinstance(deadline, int | float):
                raise ValueError("Invalid invocation deadline")
            if not math.isfinite(deadline) or deadline <= time.monotonic():
                raise ValueError("Invocation deadline has expired or is invalid")
        return Invocation(grant, None if deadline is None else float(deadline))

    @staticmethod
    def _check_protocol(context: ServerRequestContext[object]) -> None:
        if context.protocol_version != PROTOCOL_VERSION:
            raise ValueError("Unsupported component protocol")

    @staticmethod
    def _tool(operation: Operation) -> types.Tool:
        return types.Tool(
            name=operation.name,
            input_schema=operation.input_schema,
            output_schema=operation.output_schema,
        )


def create_server(component: HostedComponent, name: str, version: str) -> Server[object]:
    handler = ComponentServer(component)
    return Server(
        name, version=version, on_list_tools=handler.list_tools, on_call_tool=handler.call_tool
    )


async def serve_stdio(component: HostedComponent, name: str, version: str) -> None:
    server = create_server(component, name, version)
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def run_stdio(component: HostedComponent, name: str, version: str) -> None:
    asyncio.run(serve_stdio(component, name, version))
