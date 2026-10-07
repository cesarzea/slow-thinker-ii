"""Readiness: the pinned protocol, tools as the only capability, exactly one tool."""

from typing import cast

from mcp import Client, types
from mcp.shared.exceptions import MCPError

from slow_thinker_ii.engine import Position

from ._process import HostProcess
from ._protocol import PROTOCOL_VERSION, protocol_tools


class NotReady(Exception):
    """Why a host is not ready; `cause` completes "<Component> in <Node> could not start:"."""

    def __init__(self, code: str, cause: str) -> None:
        super().__init__(cause)
        self.code = code
        self.cause = cause


async def require_ready(client: Client, position: Position) -> None:
    """Raises NotReady unless discovery and the tool list are exactly the protocol's."""
    discovered = await client.session.send_request(types.DiscoverRequest(), types.DiscoverResult)
    if PROTOCOL_VERSION not in discovered.supported_versions:
        cause = f"it does not support the MCP protocol {PROTOCOL_VERSION}."
        raise NotReady("protocol_error", cause)
    capabilities = sorted(discovered.capabilities.model_dump(exclude_none=True, by_alias=True))
    if capabilities != ["tools"]:
        listed = ", ".join(capabilities) or "nothing"
        raise NotReady("protocol_error", f"it offers {listed} instead of tools only.")
    listing = await client.list_tools()
    expected = list(protocol_tools(position))
    tools = [(tool.name, tool.input_schema, tool.output_schema) for tool in listing.tools]
    if listing.next_cursor is None and sorted(tools) == sorted(expected):
        return
    names = sorted(tool.name for tool in listing.tools)
    wanted = sorted(name for name, _, _ in expected)
    served = " and ".join(wanted)
    noun = "tool" if len(wanted) == 1 else "tools"
    if names == wanted:
        verb = "does" if len(wanted) == 1 else "do"
        cause = f"its {served} {noun} {verb} not have the protocol's schemas."
    else:
        listed = ", ".join(names) or "no tools"
        cause = f"it exposes {listed} instead of only the {served} {noun}."
    raise NotReady("tools_mismatch", cause)


def startup_failure(error: Exception, process: HostProcess) -> NotReady:
    """The reason a host's start failed with `error`, once its process is stopped."""
    if isinstance(error, NotReady):
        return error
    problem = process.diagnostics.problem
    if problem == "oversized":
        return NotReady("protocol_error", "it sent a message above the size limit.")
    if problem is not None:
        return NotReady("protocol_error", "it wrote output that is not the protocol's JSON-RPC.")
    if process.returncode is None:
        return NotReady("launch_failed", f"its interpreter could not be started: {error}.")
    if isinstance(error, MCPError) and error.code == types.CONNECTION_CLOSED:
        status = f"it exited with status {process.returncode} before it was ready."
        return NotReady("exited", process.diagnostics.last_line() or status)
    reason = error.message if isinstance(error, MCPError) else f"{type(error).__name__}: {error}"
    return NotReady("protocol_error", f"it failed the protocol handshake: {reason}.")


def unwrap(error: BaseException) -> BaseException:
    """The single exception inside nested one-member exception groups."""
    current = error
    while isinstance(current, BaseExceptionGroup):
        members = cast(BaseExceptionGroup[BaseException], current).exceptions
        if len(members) != 1:
            break
        current = members[0]
    return cast(BaseException, current)
