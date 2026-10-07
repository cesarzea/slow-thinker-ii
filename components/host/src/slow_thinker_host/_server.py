"""MCP handlers of one host: its protocol tool, call budgets, concurrency and errors."""

import asyncio
import sys
import traceback
from collections.abc import Awaitable, Callable

from mcp import types
from mcp.server import ServerRequestContext
from mcp.shared.exceptions import MCPError

from ._bootstrap import Bootstrap
from ._calls import CallMeta, call_meta, describe, tool_error, tool_result
from ._context import Context, InvocationContext
from ._json import JsonObject, json_object
from ._protocol import PROTOCOL_VERSION, HandlerError, position_tools
from ._schemas import validate_value

type Invoke = Callable[[JsonObject, Context], Awaitable[JsonObject]]


class HostServer:
    """Serves the position's tools; waiting for a free slot counts against the budget."""

    def __init__(self, bootstrap: Bootstrap, invokes: dict[str, Invoke], stateful: bool) -> None:
        self._bootstrap = bootstrap
        self._invokes = invokes
        tools = position_tools(bootstrap.position)
        self._tools = {name: (inputs, outputs) for name, inputs, outputs in tools}
        self._slots = asyncio.Semaphore(1 if stateful else bootstrap.max_concurrent_invocations)

    async def list_tools(
        self, context: ServerRequestContext[object], params: types.PaginatedRequestParams | None
    ) -> types.ListToolsResult:
        del params
        _require_protocol(context)
        tools = [
            types.Tool(name=name, input_schema=inputs, output_schema=outputs)
            for name, inputs, outputs in position_tools(self._bootstrap.position)
        ]
        return types.ListToolsResult(tools=tools)

    async def call_tool(
        self, context: ServerRequestContext[object], params: types.CallToolRequestParams
    ) -> types.CallToolResult:
        _require_protocol(context)
        try:
            call, arguments = self._accept(context, params)
            value = await self._run(params.name, call, arguments)
        except HandlerError as error:
            return tool_error(error.code, error.message)
        return tool_result(value)

    def _accept(
        self, context: ServerRequestContext[object], params: types.CallToolRequestParams
    ) -> tuple[CallMeta, JsonObject]:
        schemas = self._tools.get(params.name)
        if schemas is None:
            served = ", ".join(self._tools)
            raise HandlerError("unknown_tool", f"This host serves only {served}.")
        call = call_meta(context.meta)
        try:
            arguments = json_object(params.arguments or {})
            validate_value(arguments, schemas[0])
        except ValueError as error:
            message = f"The arguments do not match the {params.name} schema: {error}"
            raise HandlerError("invalid_arguments", message) from error
        return call, arguments

    async def _run(self, tool: str, call: CallMeta, arguments: JsonObject) -> JsonObject:
        deadline = asyncio.get_running_loop().time() + call.budget_seconds
        context = InvocationContext(self._bootstrap, call, deadline)
        budget = asyncio.timeout(call.budget_seconds)
        try:
            async with budget, self._slots:
                value = await self._invokes[tool](arguments, context)
        except HandlerError:
            raise
        except TimeoutError as error:
            raise _expiry(budget, call, error) from error
        except Exception as error:
            self._log(tool, error)
            raise HandlerError("component_error", describe(error)) from error
        finally:
            await context.close()
        return self._checked(tool, value)

    def _log(self, tool: str, error: Exception) -> None:
        """Unexpected exceptions keep their traceback in the host's standard error."""
        header = f"Node {self._bootstrap.node_id}: {tool} raised an unexpected exception\n"
        sys.stderr.write(header + "".join(traceback.format_exception(error)))

    def _checked(self, tool: str, value: JsonObject) -> JsonObject:
        try:
            validate_value(value, self._tools[tool][1])
        except ValueError as error:
            message = f"The result does not match the {tool} schema: {error}"
            raise HandlerError("invalid_result", message) from error
        return value


def _expiry(budget: asyncio.Timeout, call: CallMeta, error: TimeoutError) -> HandlerError:
    if not budget.expired():
        return HandlerError("component_error", describe(error))
    milliseconds = round(call.budget_seconds * 1000)
    return HandlerError("timeout", f"The call exceeded its time budget of {milliseconds} ms.")


def _require_protocol(context: ServerRequestContext[object]) -> None:
    if context.protocol_version != PROTOCOL_VERSION:
        raise MCPError(code=types.INVALID_REQUEST, message="Unsupported component protocol")
