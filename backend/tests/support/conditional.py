"""Deterministic bounded operations exercise production compilation, scheduling and evidence."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager

from slow_thinker_bounded_flow import BoundedFlow, CompletedStep, parse_config
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.catalog import ConditionalCompiler
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence, OperationPort, OperationReply
from slow_thinker_ii.contracts import (
    JsonObject,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_ii.definitions import ConditionalPlan

from .managed_calls import FixtureOperation
from .sequence_plans import SCHEMAS, graph_value, resolved


def conditional_plan(problem: str = "accept") -> ConditionalPlan:
    graph = graph_value("bounded-review")
    return ConditionalCompiler(SCHEMAS).compile(
        encode_json(graph), encode_json({"problem": problem}), resolved(graph)
    )


class Controller(FixtureOperation):
    def __init__(self, plan: ConditionalPlan) -> None:
        super().__init__()
        graph = json_object(decode_json(plan.graph_json))
        config = json_object(json_object(graph["components"])[plan.controller.component])["config"]
        self.flow = BoundedFlow(parse_config(json_object(config)))

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        value = json_object(decode_json(arguments_json))["completed"]
        assert isinstance(value, list)
        history = tuple(
            CompletedStep(str(json_object(item)["node"]), str(json_object(item)["port"]))
            for item in value
        )
        decision = self.flow.next(history)
        payload: JsonObject = {"action": decision.action}
        if decision.node is not None:
            payload["nodes"] = [decision.node]
        if decision.reason is not None:
            payload["reason"] = decision.reason
        self.result = OperationResult(encode_json(payload), False)
        return await super().invoke(arguments_json, grant, deadline)


class Participant(FixtureOperation):
    def __init__(self, mode: str, *, reviewer: bool = False) -> None:
        super().__init__(ChargeBasis(100, "fixture", "{}"), ChargeEvidence("{}", 75, "fixture"))
        self.mode, self.reviewer = mode, reviewer
        if mode == "wait" and not reviewer:
            self.release.clear()

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        count = len(self.calls) + 1
        payload: JsonObject = {"status": "ok", "format": "text", "value": f"Proposal {count}"}
        if self.reviewer:
            accepted = self.mode == "accept-immediately" or (self.mode != "exhaust" and count > 1)
            port = "unknown" if self.mode == "bad-port" else ("accept" if accepted else "revise")
            payload = {
                "status": "succeeded",
                "port": port,
                "value": {
                    "status": "ok",
                    "format": "json",
                    "value": {
                        "accepted": accepted,
                        "findings": [] if accepted else [f"Finding {count}"],
                    },
                },
            }
        self.result = OperationResult(encode_json(payload), False)
        return await super().invoke(arguments_json, grant, deadline)


class ConditionalEnvironment:
    def __init__(self, plan: ConditionalPlan, mode: str = "accept") -> None:
        self.proposer, self.reviewer = Participant(mode), Participant(mode, reviewer=True)
        self.controller = Controller(plan)
        self.operations: Mapping[OperationAddress, OperationPort] = {
            OperationAddress("proposer", "generate"): self.proposer,
            OperationAddress("reviewer", "invoke"): self.reviewer,
            OperationAddress(plan.controller.component, plan.controller.operation): self.controller,
        }

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        assert deadline > 0
        yield self.operations

    def report(self) -> str:
        return "[]"
