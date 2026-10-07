"""Stateless hosts run up to their limit at once; stateful hosts run one call at a time."""

import asyncio

import pytest
from host_fixtures import Recorder, bootstrap, connect, meta
from slow_thinker_host import create_server


async def _held_calls(handler: Recorder, *, concurrency: int, stateful: bool) -> list[object]:
    handler.release.clear()
    server = create_server(bootstrap(concurrency=concurrency), node=handler, stateful=stateful)
    async with connect(server) as client:
        calls = [
            asyncio.create_task(client.call_tool("activate", {"message": index}, meta=meta()))
            for index in range(5)
        ]
        while handler.running < (1 if stateful else concurrency):
            await asyncio.sleep(0.005)
        await asyncio.sleep(0.05)
        started = len(handler.messages)
        handler.release.set()
        results = await asyncio.gather(*calls)
    return [started, *(result.structured_content for result in results)]


@pytest.mark.parametrize(("stateful", "limit"), [(False, 2), (True, 1)])
async def test_further_calls_wait_for_a_slot_instead_of_failing(stateful: bool, limit: int) -> None:
    handler = Recorder()
    started, *results = await _held_calls(handler, concurrency=2, stateful=stateful)
    assert started == limit and handler.peak == limit
    assert results == [{"emissions": [{"port": "out", "payload": index}]} for index in range(5)]


async def test_stateful_hosts_ignore_the_concurrency_limit() -> None:
    handler = Recorder()
    started, *_ = await _held_calls(handler, concurrency=4, stateful=True)
    assert started == 1 and handler.peak == 1
