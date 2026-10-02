"""Simulate participants while preserving declared Sequence scheduling and node evidence."""

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence, OperationPort, OperationReply
from slow_thinker_ii.contracts import OperationResult, decode_json, encode_json, json_object
from slow_thinker_ii.definitions import SequencePlan
from slow_thinker_sequence import Sequence

from .managed_calls import FixtureOperation
from .sequence_plans import STRINGS


class BrowserSequenceController(FixtureOperation):
    def __init__(self, plan: SequencePlan) -> None:
        super().__init__()
        self.sequence = Sequence(tuple(node.node_id for node in plan.nodes))

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        value = json_object(decode_json(arguments_json))["completed_nodes"]
        decision = self.sequence.next(STRINGS.validate_python(value))
        self.result = OperationResult(
            encode_json({"action": decision.action, "nodes": list(decision.nodes)}), False
        )
        return await super().invoke(arguments_json, grant, deadline)


class BrowserSequenceEnvironment:
    def __init__(self, plan: SequencePlan, problem: str) -> None:
        controller = plan.controller
        self.operations: dict[OperationAddress, OperationPort] = {
            OperationAddress(controller.component, controller.operation): BrowserSequenceController(
                plan
            )
        }
        for node in plan.nodes:
            operation = FixtureOperation(
                ChargeBasis(3000, "fixture", "{}"),
                ChargeEvidence("{}", 2390, "browser-fixture"),
            )
            operation.result = OperationResult(
                '{"status":"ok","format":"text","value":"Test result"}', False
            )
            if problem == "wait":
                operation.release.clear()
            self.operations[OperationAddress(node.target.component, node.target.operation)] = (
                operation
            )

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncGenerator[Mapping[OperationAddress, OperationPort]]:
        assert deadline > 0
        yield self.operations

    def report(self) -> str:
        return "[]"
