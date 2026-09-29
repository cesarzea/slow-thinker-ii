"""Public authenticated MCP gateway records contain no transport or SDK objects."""

from dataclasses import dataclass
from typing import Protocol

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.contracts import OperationContract

from ._dispatch_ports import ManagedResult


@dataclass(frozen=True)
class GatewayOperation:
    address: OperationAddress
    contract: OperationContract


@dataclass(frozen=True)
class GatewayTool:
    alias: str
    address: OperationAddress
    contract: OperationContract


class RejectionRecorder(Protocol):
    def reject(self, grant: str, requested_operation: str, reason: str) -> None: ...


class ManagedGatewayService(RejectionRecorder, Protocol):
    def deadline(self, grant: str) -> float: ...
    def tools(self, grant: str) -> tuple[GatewayTool, ...]: ...
    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult: ...
    def report(self, grant: str, report_json: str) -> None: ...
