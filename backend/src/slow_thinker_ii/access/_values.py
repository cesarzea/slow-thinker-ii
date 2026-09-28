"""Immutable permission, limit and invocation values; credentials stay transient."""

import math
from dataclasses import dataclass, field


class AccessDenied(PermissionError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, order=True)
class OperationAddress:
    instance: str
    operation: str

    def __post_init__(self) -> None:
        if not self.instance or not self.operation:
            raise ValueError("Operation identities must be non-empty")


@dataclass(frozen=True)
class Permission:
    caller: str
    target: OperationAddress


@dataclass(frozen=True)
class PublishedOperation:
    alias: str
    address: OperationAddress


@dataclass(frozen=True)
class CallLimits:
    max_calls: int
    max_depth: int
    call_seconds: float

    def __post_init__(self) -> None:
        for count in (self.max_calls, self.max_depth):
            if type(count) is not int or count < 1:
                raise ValueError("Call and depth bounds must be positive integers")
        if isinstance(self.call_seconds, bool) or not math.isfinite(self.call_seconds):
            raise ValueError("Call duration must be finite")
        if self.call_seconds <= 0:
            raise ValueError("Call duration must be positive")


@dataclass(frozen=True)
class CallContext:
    run_id: str
    graph_revision: str
    activation_id: str | None
    call_id: str
    attempt_id: str
    parent_call_id: str | None
    caller: str | None
    target: OperationAddress
    depth: int
    deadline: float
    node_id: str | None = None


@dataclass(frozen=True)
class InvocationLease:
    context: CallContext
    token: str = field(repr=False)


@dataclass(frozen=True)
class InvocationEnd:
    call_id: str
    publish: bool
    reason: str | None
    revoked: tuple[str, ...]
