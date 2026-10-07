"""The MCP transport of one host: its process, the three pumps and a bounded shutdown."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.shared.message import SessionMessage

from ._process import HostProcess
from ._pumps import drain, receive, send

type Streams = tuple[
    MemoryObjectReceiveStream[SessionMessage | Exception], MemoryObjectSendStream[SessionMessage]
]

STDERR_SECONDS = 1.0


@asynccontextmanager
async def transport(process: HostProcess) -> AsyncGenerator[Streams]:
    """Starts the process; on exit stops it, even when cancelled, keeping its pipes drained."""
    child = await process.start()
    try:
        stdin, stdout, stderr = child.stdin, child.stdout, child.stderr
        assert stdin is not None and stdout is not None and stderr is not None, "piped host"
        incoming, read = anyio.create_memory_object_stream[SessionMessage | Exception](0)
        write, outgoing = anyio.create_memory_object_stream[SessionMessage](0)
        diagnostics, ended = process.diagnostics, anyio.Event()
        async with incoming, read, write, outgoing, anyio.create_task_group() as group:
            group.start_soon(receive, stdout, incoming, diagnostics)
            group.start_soon(send, outgoing, stdin)
            group.start_soon(drain, stderr, diagnostics, ended)
            try:
                yield read, write
            finally:
                with anyio.CancelScope(shield=True):
                    await process.stop()
                    with anyio.move_on_after(STDERR_SECONDS):
                        await ended.wait()
                group.cancel_scope.cancel()
    finally:
        with anyio.CancelScope(shield=True):
            await process.stop()
