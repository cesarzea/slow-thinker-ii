"""One host: its process and MCP session live in a task of their own until `stop`."""

import asyncio
from contextlib import suppress

import anyio
from mcp import Client, types
from mcp.shared.exceptions import MCPError

from slow_thinker_ii.contracts import JsonObject, encode_json
from slow_thinker_ii.engine import CallContext, CallFailure, Position

from ._process import HostProcess
from ._protocol import PROTOCOL_VERSION, call_meta
from ._readiness import NotReady, require_ready, startup_failure, unwrap
from ._transport import transport

ENVELOPE_BYTES = 4096  # room for the JSON-RPC envelope and `_meta` around the arguments
GRACE_SECONDS = 0.5  # the engine's own timers decide `timeout` or `time_limit` before this
BROKEN = (MCPError, RuntimeError, anyio.ClosedResourceError, anyio.BrokenResourceError)

type Reply = types.CallToolResult | CallFailure


class Host:
    """A started host serves calls from any task; a broken one answers with failures."""

    def __init__(self, process: HostProcess, position: Position, startup_seconds: float) -> None:
        self._process = process
        self._position: Position = position
        self._startup_seconds = startup_seconds
        self._client: Client | None = None
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Returns once the host is ready; otherwise stops it and raises NotReady."""
        ready: asyncio.Future[Client] = asyncio.get_running_loop().create_future()
        self._task = asyncio.create_task(self._serve(ready))
        try:
            async with asyncio.timeout(self._startup_seconds):
                self._client = await asyncio.shield(ready)
        except TimeoutError:
            await self.stop()
            cause = f"it was not ready within {self._startup_seconds:g} seconds."
            raise NotReady("not_ready", cause) from None
        except Exception as error:
            await self.stop()
            raise startup_failure(error, self._process) from None
        except asyncio.CancelledError:
            await self.stop()
            raise

    async def call(self, tool: str, arguments: JsonObject, context: CallContext) -> Reply:
        """One `tools/call`, waiting at most the budget plus a grace; cancelling it cancels it."""
        client, task = self._client, self._task
        if client is None or task is None or task.done():
            return CallFailure("host_failed", "The component host is not running.")
        size = len(encode_json(arguments).encode()) + ENVELOPE_BYTES
        if size > self._process.launch.max_message_bytes:
            return self._too_large(size)
        meta = call_meta(context)
        params = types.CallToolRequestParams(name=tool, arguments=arguments, _meta=meta)
        try:
            async with asyncio.timeout(context.budget_ms / 1000 + GRACE_SECONDS):
                request = types.CallToolRequest(params=params)
                return await client.session.send_request(request, types.CallToolResult)
        except TimeoutError:
            message = f"The component did not answer within {context.budget_ms} ms."
            return CallFailure("timeout", message)
        except BROKEN as error:
            return self._broken(error)
        except ValueError:
            message = f"The component's reply to {tool} is not a valid tool result."
            return CallFailure("invalid_result", message)

    async def stop(self) -> None:
        """Cancels the host's task, which stops the process within its shutdown budget."""
        task = self._task
        if task is not None:
            task.cancel()
            await asyncio.wait({task}, timeout=self._process.launch.shutdown_seconds + 1)

    async def _serve(self, ready: asyncio.Future[Client]) -> None:
        session = Client(transport(self._process), mode=PROTOCOL_VERSION, cache=None)
        try:
            async with session as client:
                await require_ready(client, self._position)
                ready.set_result(client)
                await asyncio.Event().wait()
        except Exception as error:
            failure = unwrap(error)
            with suppress(asyncio.InvalidStateError):  # failures after readiness end the host
                ready.set_exception(failure if isinstance(failure, Exception) else error)

    def _broken(self, error: Exception) -> CallFailure:
        if self._process.diagnostics.problem == "oversized":
            return self._too_large(None)
        reason = (
            error.message if isinstance(error, MCPError) else str(error) or type(error).__name__
        )
        return CallFailure("host_failed", f"The component host stopped answering: {reason}.")

    def _too_large(self, size: int | None) -> CallFailure:
        limit = self._process.launch.max_message_bytes
        carried = "" if size is None else f" of about {size} bytes"
        message = f"A message{carried} exceeds the protocol limit of {limit} bytes."
        return CallFailure("message_too_large", message)
