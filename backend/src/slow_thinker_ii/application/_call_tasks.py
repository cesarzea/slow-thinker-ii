"""Own every managed task and retain pending cleanup without extending call deadlines."""

import asyncio
from collections.abc import Coroutine

from slow_thinker_ii.access import AccessDenied, CallAuthority, CallContext, InvocationLease

from ._dispatch_ports import ManagedResult


class CallTasks:
    def __init__(self) -> None:
        self._tasks: dict[str, tuple[InvocationLease, asyncio.Task[ManagedResult]]] = {}

    def start(
        self,
        lease: InvocationLease,
        work: Coroutine[None, None, ManagedResult],
    ) -> asyncio.Task[ManagedResult]:
        task = asyncio.create_task(work)
        self._tasks[lease.context.call_id] = (lease, task)
        return task

    def forget(self, call_id: str) -> None:
        self._tasks.pop(call_id, None)

    def pending(self) -> tuple[CallContext, ...]:
        return tuple(lease.context for lease, task in self._tasks.values() if not task.done())

    def cancel_revoked(self, authority: CallAuthority, except_id: str | None = None) -> None:
        for identity, (lease, task) in self._tasks.items():
            if identity == except_id or task.done() or task.cancelling():
                continue
            try:
                authority.context(lease.token)
            except AccessDenied:
                task.cancel()

    async def drain(self, timeout: float) -> tuple[CallContext, ...]:
        tasks = tuple(task for _, task in self._tasks.values() if not task.done())
        if tasks:
            await asyncio.wait(tasks, timeout=timeout)
        return self.pending()
