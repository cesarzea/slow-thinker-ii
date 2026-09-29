"""Filtered component discovery and calls share the ordinary managed invocation path."""

from slow_thinker_ii.access import AccessDenied, CallAuthority

from ._dispatch_ports import ManagedResult
from ._gateway_records import GatewayOperation, GatewayTool
from ._native_records import GatewayError, InvocationRouter
from ._run_evidence import RunEvidence


class ManagedGateway:
    def __init__(
        self,
        authority: CallAuthority,
        calls: InvocationRouter,
        operations: tuple[GatewayOperation, ...],
        evidence: RunEvidence,
    ) -> None:
        self._authority, self._calls, self._evidence = authority, calls, evidence
        self._operations = {item.address: item.contract for item in operations}
        if len(self._operations) != len(operations):
            raise ValueError("Gateway operation addresses must be unique")

    def deadline(self, grant: str) -> float:
        return self._authority.context(grant).deadline

    def tools(self, grant: str) -> tuple[GatewayTool, ...]:
        return tuple(
            GatewayTool(item.alias, item.address, self._operations[item.address])
            for item in self._authority.discover(grant)
        )

    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult:
        try:
            result = await self._calls.invoke(grant, alias, arguments_json)
            if not result.outcome.publish and not result.result.is_error:
                raise GatewayError("managed_result_unavailable", 409)
            return result
        except AccessDenied as error:
            self.reject(grant, alias, error.code)
            raise

    def report(self, grant: str, report_json: str) -> None:
        self._evidence.report(grant, report_json)

    def reject(self, grant: str, requested_operation: str, reason: str) -> None:
        self._evidence.reject(grant, requested_operation, reason)
