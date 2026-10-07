"""Cancellation and the time budget release the response without another provider attempt."""

import asyncio
from collections.abc import AsyncIterator

import httpx
import pytest
from support.examples import FLASH

from .fixtures import chat, error_of, http_provider, model


class WaitingBody(httpx.AsyncByteStream):
    """A response body that never arrives."""

    def __init__(self) -> None:
        self.reading, self.closed = asyncio.Event(), False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        self.reading.set()
        await asyncio.Event().wait()
        yield b"unreachable"

    async def aclose(self) -> None:
        self.closed = True


@pytest.mark.parametrize("cancel", [False, True])
async def test_an_interrupted_body_closes_the_stream_after_one_attempt(cancel: bool) -> None:
    stream = WaitingBody()
    provider, exchanges = http_provider(lambda request: httpx.Response(200, stream=stream))
    reply = provider.complete(model(FLASH), chat(FLASH), 5 if cancel else 0.25)
    task = asyncio.create_task(reply)
    await asyncio.wait_for(stream.reading.wait(), 1)
    if cancel:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        answer = await task
        assert (answer.status, error_of(answer)["code"]) == (504, "provider_timeout")
    assert stream.closed and len(exchanges.requests) == 1
