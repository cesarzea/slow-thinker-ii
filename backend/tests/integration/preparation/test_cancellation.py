"""Cancellation retains ownership of bounded metadata work and never launches business hosts."""

import asyncio
import threading

import pytest
from slow_thinker_ii.adapters.preparation import HostProfile, HostRequest, PlainHostAdapter
from support.preparation import PreparationCase


class BlockingAdapter:
    def __init__(self, *, fail: bool) -> None:
        self.entered, self.release = threading.Event(), threading.Event()
        self.fail = fail

    def configure(self, request: HostRequest) -> HostProfile:
        self.entered.set()
        if not self.release.wait(5):
            raise TimeoutError("Test metadata adapter not released")
        if self.fail:
            raise ValueError("Synthetic metadata failure")
        return PlainHostAdapter().configure(request)


@pytest.mark.parametrize("fail", [False, True])
async def test_cancelled_preparation_waits_for_metadata_worker(
    case: PreparationCase, fail: bool
) -> None:
    adapter = BlockingAdapter(fail=fail)
    case.adapters["mcp"] = adapter
    task = asyncio.create_task(case.preparer().prepare(case.intent, "runtime"))
    try:
        assert await asyncio.to_thread(adapter.entered.wait, 5)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
    finally:
        adapter.release.set()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(task, 5)
    assert not (case.directory / "runtime").exists()
