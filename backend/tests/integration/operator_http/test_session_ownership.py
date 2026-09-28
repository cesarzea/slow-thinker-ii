"""A cancelled browser waiter cannot orphan an in-flight saved-session transaction."""

import asyncio
import threading

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore
from slow_thinker_ii.application import CommandResult
from support.operator_http import HttpCase


async def test_session_commit_remains_owned_during_shutdown(
    api: HttpCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    entered, release = threading.Event(), threading.Event()
    original = SqliteOperatorStore.create_session

    def delayed(self: SqliteOperatorStore, command: str, name: str) -> CommandResult:
        entered.set()
        assert release.wait(5)
        return original(self, command, name)

    monkeypatch.setattr(SqliteOperatorStore, "create_session", delayed)
    body = {"schema_version": "0.1-draft", "command_id": "delayed-session", "name": "Test"}
    waiter = asyncio.create_task(api.client.post("/api/v1/sessions", json=body))
    try:
        assert await asyncio.to_thread(entered.wait, 5)
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
        assert "session:delayed-session" in api.case.coordinator.pending().commands
        closing = asyncio.create_task(api.case.coordinator.close())
        await asyncio.sleep(0)
        assert not closing.done()
    finally:
        release.set()
    assert not (await closing).commands
    assert api.case.commands.command("delayed-session") is not None
