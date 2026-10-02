"""Cancellation and capture deadline release resources without another provider attempt."""

import asyncio
from collections.abc import AsyncIterator

import httpx2
import pytest
from model_provider_fixture import SECRET, invocation
from slow_thinker_model_provider import ProviderEndpoint, ProviderTransport


class WaitingBody(httpx2.AsyncByteStream):
    def __init__(self) -> None:
        self.reading, self.closed = asyncio.Event(), False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.reading.set()
        await asyncio.Event().wait()
        yield b"unreachable"

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.parametrize("cancel", [False, True])
async def test_interrupted_capture_closes_stream_and_keeps_single_attempt(cancel: bool) -> None:
    stream = WaitingBody()
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        return httpx2.Response(200, stream=stream)

    transport = ProviderTransport(
        ProviderEndpoint("deepseek", "https://api.deepseek.com", SECRET),
        httpx2.MockTransport(handle),
    )
    task = asyncio.create_task(transport.complete({}, invocation(5 if cancel else 0.05)))
    await asyncio.wait_for(stream.reading.wait(), 1)
    if cancel:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        reply = await task
        assert reply.is_error and "provider_outcome_unknown" in str(reply.value)
    assert stream.closed and len(calls) == 1
