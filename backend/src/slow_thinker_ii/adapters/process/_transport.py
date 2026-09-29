"""Transport context owns pipes, pumps and the component process together."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from anyio import create_memory_object_stream
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp.shared.message import SessionMessage

from ._diagnostics import capture_diagnostics
from ._launch import ProcessLaunch
from ._owned import OwnedProcess
from ._pumps import receive, send

type Streams = tuple[
    MemoryObjectReceiveStream[SessionMessage | Exception], MemoryObjectSendStream[SessionMessage]
]


@asynccontextmanager
async def transport(owner: OwnedProcess, launch: ProcessLaunch) -> AsyncIterator[Streams]:
    process = await owner.start()
    try:
        async with channels(process, launch) as streams:
            yield streams
    finally:
        await owner.stop()


@asynccontextmanager
async def channels(
    process: asyncio.subprocess.Process, launch: ProcessLaunch
) -> AsyncIterator[Streams]:
    limit = launch.max_message_bytes
    if process.stdout is None or process.stdin is None or process.stderr is None:
        raise RuntimeError("Component pipes are missing")
    incoming, read = create_memory_object_stream[SessionMessage | Exception](0)
    write, outgoing = create_memory_object_stream[SessionMessage](0)
    async with incoming, read, write, outgoing, asyncio.TaskGroup() as group:
        tasks = (
            group.create_task(receive(process.stdout, incoming, limit)),
            group.create_task(send(outgoing, process.stdin, limit)),
            group.create_task(capture_diagnostics(process.stderr, launch)),
        )
        try:
            yield read, write
        finally:
            for task in tasks:
                task.cancel()
