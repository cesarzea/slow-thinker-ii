"""Newline-delimited JSON-RPC between MCP streams and host pipes; inbound lines are bounded."""

import asyncio

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import types
from mcp.shared.message import SessionMessage

from ._process import Diagnostics


async def receive(
    reader: asyncio.StreamReader,
    sink: MemoryObjectSendStream[SessionMessage | Exception],
    diagnostics: Diagnostics,
) -> None:
    """Delivers each line as a message; an oversized or invalid line ends the connection."""
    async with sink:
        while True:
            try:
                line = await reader.readline()
            except ValueError:
                diagnostics.problem = "oversized"
                await sink.send(ValueError("The host sent a message above the size limit"))
                return
            if not line:
                return
            try:
                message = types.jsonrpc_message_adapter.validate_json(line, by_name=False)
            except ValueError:
                diagnostics.problem = "invalid"
                await sink.send(ValueError("The host sent a line that is not JSON-RPC"))
                return
            await sink.send(SessionMessage(message))


async def send(
    source: MemoryObjectReceiveStream[SessionMessage], writer: asyncio.StreamWriter
) -> None:
    """Writes each message as one line. Once the pipe breaks, later messages are refused."""
    async with source:
        async for message in source:
            data = message.message.model_dump_json(by_alias=True, exclude_unset=True)
            try:
                writer.write((data + "\n").encode())
                await writer.drain()
            except (ConnectionError, OSError):
                return


async def drain(reader: asyncio.StreamReader, diagnostics: Diagnostics, ended: anyio.Event) -> None:
    """Keeps the end of standard error, so that a chatty host never blocks on it."""
    try:
        while chunk := await reader.read(8192):
            diagnostics.add(chunk)
    finally:
        ended.set()
