"""Command ownership survives cancelled HTTP waiters without duplicating a pending intention."""

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, replace

from ._operator_ports import CoordinatorUnavailable
from ._operator_records import CommandConflict, CommandResult


@dataclass(frozen=True)
class PendingCommand:
    body: str
    task: asyncio.Task[CommandResult]


class CommandJobs:
    def __init__(self, maximum: int) -> None:
        self._maximum = maximum
        self._pending: dict[str, PendingCommand] = {}

    async def submit(
        self, key: str, body: str, factory: Callable[[], Coroutine[None, None, CommandResult]]
    ) -> CommandResult:
        existing = self._pending.get(key)
        if existing is not None:
            if existing.body != body:
                raise CommandConflict("command_conflict")
            return replace(await asyncio.shield(existing.task), replayed=True)
        if len(self._pending) >= self._maximum:
            raise CoordinatorUnavailable("pending_command_limit")
        task = asyncio.create_task(factory())
        self._pending[key] = PendingCommand(body, task)
        task.add_done_callback(lambda completed: self._finished(key, completed))
        return await asyncio.shield(task)

    def _finished(self, key: str, task: asyncio.Task[CommandResult]) -> None:
        self._pending.pop(key, None)
        if not task.cancelled():
            task.exception()

    def tasks(self) -> tuple[asyncio.Task[CommandResult], ...]:
        return tuple(item.task for item in self._pending.values())

    def pending(self) -> tuple[str, ...]:
        return tuple(key for key, item in self._pending.items() if not item.task.done())
