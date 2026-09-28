"""Bind a ready MCP operation to validation, pricing and one transport invocation."""

import json
import time

from jsonschema import ValidationError
from mcp.shared.exceptions import MCPError

from slow_thinker_ii.application import (
    ChargeEvidence,
    OperationReply,
    PreparedOperation,
    PricingPolicy,
)
from slow_thinker_ii.contracts import OperationResult

from ._connection import ComponentConnection


class ProcessOperation:
    def __init__(
        self, connection: ComponentConnection, name: str, pricing: PricingPolicy | None
    ) -> None:
        self._connection, self._name, self._pricing = connection, name, pricing

    def prepare(self, arguments_json: str) -> PreparedOperation:
        try:
            arguments = self._connection.prepare(self._name, arguments_json)
        except ValidationError as error:
            raise ValueError("Invalid operation arguments") from error
        charge = None if self._pricing is None else self._pricing.quote(arguments)
        return PreparedOperation(arguments, charge)

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        try:
            result = await self._connection.call(
                self._name, arguments_json, grant, deadline - time.monotonic(), deadline=deadline
            )
        except MCPError as error:
            result = OperationResult(
                json.dumps(
                    {
                        "error": {
                            "origin": "component",
                            "code": error.code,
                            "message": error.message,
                            "data": error.data,
                        }
                    }
                ),
                True,
            )
        return OperationReply(result, self._reconcile(result))

    def _reconcile(self, result: OperationResult) -> ChargeEvidence | None:
        if self._pricing is None:
            return None
        try:
            return self._pricing.reconcile(result)
        except Exception as error:
            diagnostic = json.dumps(
                {
                    "status": "unavailable",
                    "origin": "platform",
                    "reason": "pricing_failed",
                    "error_type": type(error).__name__,
                }
            )
            return ChargeEvidence(diagnostic, None, "pricing_adapter")
