"""Bounded stdio framing around SDK protocol objects, without logging credentials."""

import asyncio

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from mcp import types
from mcp.shared.message import SessionMessage
from pydantic import TypeAdapter

MESSAGE: TypeAdapter[types.JSONRPCMessage] = TypeAdapter(types.JSONRPCMessage)


async def receive(
    reader: asyncio.StreamReader,
    target: MemoryObjectSendStream[SessionMessage | Exception],
    limit: int,
) -> None:
    async with target:
        try:
            while line := await reader.readline():
                if len(line) > limit:
                    raise ValueError("Protocol frame exceeds byte limit")
                await target.send(SessionMessage(MESSAGE.validate_json(line)))
        except ValueError:
            await target.send(ValueError("Invalid or oversized component protocol frame"))


async def send(
    source: MemoryObjectReceiveStream[SessionMessage], writer: asyncio.StreamWriter, limit: int
) -> None:
    async with source:
        async for message in source:
            encoded = (
                message.message.model_dump_json(by_alias=True, exclude_none=True).encode() + b"\n"
            )
            if len(encoded) > limit:
                raise ValueError("Outgoing protocol frame exceeds byte limit")
            writer.write(encoded)
            await writer.drain()
