"""Coordinate nested component calls while all external work runs outside transactions."""

import asyncio
import math
from collections.abc import Mapping

from slow_thinker_ii.access import CallAuthority, CallContext, InvocationLease, OperationAddress

from ._call_delivery import deliver
from ._call_tasks import CallTasks
from ._dispatch_ports import ManagedResult, OperationPort
from ._run_admission import RunAdmission


class ManagedCalls:
    def __init__(
        self,
        authority: CallAuthority,
        admission: RunAdmission,
        operations: Mapping[OperationAddress, OperationPort],
    ) -> None:
        self._authority, self._admission = authority, admission
        self._operations = dict(operations)
        self._tasks = CallTasks()

    async def schedule(
        self,
        target: OperationAddress,
        arguments_json: str,
        *,
        activation: bool = True,
        node_id: str | None = None,
    ) -> ManagedResult:
        return await self._dispatch(
            self._authority.schedule(target, activation=activation, node_id=node_id), arguments_json
        )

    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult:
        return await self._dispatch(self._authority.invoke(grant, alias), arguments_json)

    async def _dispatch(self, lease: InvocationLease, arguments_json: str) -> ManagedResult:
        try:
            operation = self._prepare(lease, arguments_json)
            task = self._tasks.start(lease, deliver(self._admission, lease, operation))
            return await task
        except asyncio.CancelledError:
            self._admission.cancel(lease.context.call_id)
            raise
        finally:
            self._authority.finish(lease.context.call_id, succeeded=False)
            self._tasks.forget(lease.context.call_id)
            self._tasks.cancel_revoked(self._authority, lease.context.call_id)

    def _prepare(self, lease: InvocationLease, arguments_json: str) -> OperationPort:
        operation = self._operations.get(lease.context.target)
        try:
            if operation is None:
                raise ValueError("No ready operation is bound to this target")
            prepared = operation.prepare(arguments_json)
        except Exception as error:
            reason = (
                "invalid_operation_input"
                if isinstance(error, ValueError)
                else "operation_preparation_failed"
            )
            self._admission.reject(lease.token, arguments_json, reason)
            raise
        self._admission.reserve(lease.token, prepared.arguments_json, prepared.charge)
        return operation

    def stop(self, reason: str) -> tuple[str, ...]:
        try:
            return self._admission.stop(reason)
        finally:
            self._tasks.cancel_revoked(self._authority)

    def pending(self) -> tuple[CallContext, ...]:
        return self._tasks.pending()

    async def close(self, timeout: float) -> tuple[CallContext, ...]:
        if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Cleanup requires a positive finite timeout")
        self.stop("runtime_shutdown")
        return await self._tasks.drain(timeout)
