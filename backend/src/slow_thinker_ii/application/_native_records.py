"""Native model compatibility values keep HTTP and provider SDK objects outside use cases."""

from dataclasses import dataclass
from typing import Protocol

from slow_thinker_ii.access import OperationAddress

from ._dispatch_ports import ManagedResult


@dataclass(frozen=True)
class ModelBinding:
    caller: str
    model_alias: str
    target: OperationAddress


@dataclass(frozen=True)
class NativeReply:
    status: int
    payload_json: str
    request_id: str | None = None
    retry_after: str | None = None


class InvocationRouter(Protocol):
    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult: ...


class GatewayError(ValueError):
    def __init__(self, code: str, status: int = 502) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class NativeModelService(Protocol):
    def deadline(self, grant: str) -> float: ...
    async def complete(self, grant: str, request_json: str) -> NativeReply: ...
