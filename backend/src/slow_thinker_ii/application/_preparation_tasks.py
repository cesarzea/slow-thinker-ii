"""Bound preparation and retain cancelled tasks until they really finish."""

import asyncio

from ._operator_ports import PreparationRejected, PreparedWorkflow, WorkflowPreparer
from ._operator_records import StartIntent


class PreparationTasks:
    def __init__(self, preparer: WorkflowPreparer, seconds: float, maximum: int) -> None:
        self._preparer, self._seconds, self._maximum = preparer, seconds, maximum
        self._pending: dict[str, asyncio.Task[PreparedWorkflow]] = {}

    async def prepare(self, key: str, intent: StartIntent, runtime: str) -> PreparedWorkflow:
        if key in self._pending or len(self._pending) >= self._maximum:
            raise PreparationRejected("preparation_capacity")
        task = asyncio.create_task(self._preparer.prepare(intent, runtime))
        self._pending[key] = task
        task.add_done_callback(lambda completed: self._finished(key, completed))
        done, _ = await asyncio.wait((task,), timeout=self._seconds)
        if not done:
            task.cancel()
            raise PreparationRejected("preparation_timeout")
        if task.cancelled():
            raise PreparationRejected("preparation_cancelled")
        return task.result()

    def _finished(self, key: str, task: asyncio.Task[PreparedWorkflow]) -> None:
        self._pending.pop(key, None)
        if not task.cancelled():
            task.exception()

    def cancel(self) -> None:
        for task in self._pending.values():
            if not task.done() and not task.cancelling():
                task.cancel()

    def tasks(self) -> tuple[asyncio.Task[PreparedWorkflow], ...]:
        return tuple(self._pending.values())

    def pending(self) -> tuple[str, ...]:
        return tuple(key for key, task in self._pending.items() if not task.done())
