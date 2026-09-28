"""Serialize transient authority decisions; never hold this lock during external work."""

import math
from collections.abc import Callable
from threading import RLock

from ._active import ActiveCalls
from ._contexts import call_context
from ._policy import AccessPolicy
from ._values import (
    AccessDenied,
    CallContext,
    CallLimits,
    InvocationEnd,
    InvocationLease,
    OperationAddress,
    PublishedOperation,
)


class CallAuthority:
    def __init__(
        self,
        run_id: str,
        graph_revision: str,
        policy: AccessPolicy,
        limits: CallLimits,
        deadline: float,
        clock: Callable[[], float],
    ) -> None:
        if not run_id or not graph_revision or not math.isfinite(deadline) or deadline <= clock():
            raise ValueError("Run identity and a future finite deadline are required")
        self._run, self._revision = run_id, graph_revision
        self._policy, self._limits = policy, limits
        self._deadline, self._clock = deadline, clock
        self._active = ActiveCalls()
        self._lock = RLock()
        self._closed = False
        self._count = 0

    def schedule(
        self, target: OperationAddress, *, activation: bool = True, node_id: str | None = None
    ) -> InvocationLease:
        with self._lock:
            now = self._require_open()
            self._policy.require_scheduled(target)
            return self._admit(target, None, now, activation=activation, node_id=node_id)

    def context(self, token: str) -> CallContext:
        with self._lock:
            return self._active.authenticate(token, self._require_open())

    def discover(self, token: str) -> tuple[PublishedOperation, ...]:
        with self._lock:
            parent = self._active.authenticate(token, self._require_open())
            return self._policy.discover(parent.target.instance)

    def invoke(self, token: str, alias: str) -> InvocationLease:
        with self._lock:
            now = self._require_open()
            parent = self._active.authenticate(token, now)
            target = self._policy.resolve(parent.target.instance, alias)
            return self._admit(target, parent, now)

    def finish(self, call_id: str, *, succeeded: bool) -> InvocationEnd:
        with self._lock:
            self._active.release(call_id)
            context = self._active.contexts.get(call_id)
            if context is None:
                return InvocationEnd(call_id, False, "authority_closed", ())
            descendants = self._active.subtree(call_id)
            reason = self._completion_reason(context, descendants, succeeded)
            self._active.revoke(descendants)
            return InvocationEnd(call_id, reason is None, reason, descendants)

    def revoke(self, call_id: str) -> tuple[str, ...]:
        with self._lock:
            identities = self._active.subtree(call_id)
            self._active.revoke(identities)
            return identities

    def stop(self) -> tuple[str, ...]:
        with self._lock:
            self._closed = True
            active = self._active.executing()
            self._active.revoke(tuple(self._active.contexts))
            return active

    def _require_open(self) -> float:
        now = self._clock()
        if self._closed or now >= self._deadline:
            raise AccessDenied("run_closed")
        return now

    def _admit(
        self,
        target: OperationAddress,
        parent: CallContext | None,
        now: float,
        *,
        activation: bool = False,
        node_id: str | None = None,
    ) -> InvocationLease:
        depth = 1 if parent is None else parent.depth + 1
        if self._count >= self._limits.max_calls:
            raise AccessDenied("call_limit")
        if depth > self._limits.max_depth:
            raise AccessDenied("depth_limit")
        if self._active.busy(target.instance):
            raise AccessDenied("instance_busy")
        deadline = min(self._deadline, now + self._limits.call_seconds)
        if parent is not None:
            deadline = min(deadline, parent.deadline)
        context = call_context(
            self._run, self._revision, target, parent, depth, deadline, activation, node_id
        )
        lease = self._active.issue(context)
        self._count += 1
        return lease

    def _completion_reason(
        self,
        context: CallContext,
        descendants: tuple[str, ...],
        succeeded: bool,
    ) -> str | None:
        if self._clock() >= min(context.deadline, self._deadline):
            return "deadline_expired"
        if len(descendants) > 1:
            return "unfinished_children"
        return None if succeeded else "operation_failed"
