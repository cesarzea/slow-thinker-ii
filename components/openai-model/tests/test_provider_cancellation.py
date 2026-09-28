"""Deadline and external cancellation close the HTTP stream without retrying it."""

import asyncio
import time
from collections.abc import AsyncIterator

import httpx2
import pytest
from slow_thinker_host import Invocation
from slow_thinker_openai_model import ProviderEndpoint, ProviderTransport


class WaitingBody(httpx2.AsyncByteStream):
    def __init__(self) -> None:
        self.reading = asyncio.Event()
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.reading.set()
        await asyncio.Event().wait()
        yield b"unreachable"

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.parametrize("cancel", [False, True])
async def test_interrupted_capture_is_closed_and_never_retried(cancel: bool) -> None:
    stream = WaitingBody()
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        return httpx2.Response(200, stream=stream)

    endpoint = ProviderEndpoint("https://api.openai.com/v1", "fixture-key")
    transport = ProviderTransport(endpoint, httpx2.MockTransport(handle))
    task = asyncio.create_task(
        transport.complete({}, Invocation("grant", time.monotonic() + (5 if cancel else 0.05)))
    )
    await asyncio.wait_for(stream.reading.wait(), 1)
    if cancel:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        reply = await task
        assert reply.is_error and "provider_outcome_unknown" in str(reply.value)
    assert stream.closed and len(calls) == 1
