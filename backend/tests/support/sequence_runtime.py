"""A real sequence process drives fixture agents through the ordinary transactional runner."""

import sys
from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from jsonschema import validate
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.process import (
    ComponentProcess,
    ProcessFleet,
    ProcessHost,
    ProcessLaunch,
)
from slow_thinker_ii.application import (
    ManagedRun,
    OperationPort,
    OperationReply,
    RunFinalization,
    sequence_access,
)
from slow_thinker_ii.contracts import (
    JsonObject,
    OperationContract,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_ii.definitions import SequencePlan

from .managed_calls import FixtureOperation, RealClock
from .run_admission import RunCase, run_case


class AnswerOperation(FixtureOperation):
    def __init__(self, name: str, contract: OperationContract) -> None:
        super().__init__()
        self.name, self.contract = name, contract

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        validate(
            decode_json(arguments_json), json_object(decode_json(self.contract.input_schema_json))
        )
        self.calls.append((arguments_json, grant, deadline))
        payload: JsonObject = {
            "status": "ok",
            "format": "text",
            "value": f"{self.name}-{len(self.calls)}",
        }
        return OperationReply(OperationResult(encode_json(payload), False))


def sequence_process(directory: Path, plan: SequencePlan) -> ComponentProcess:
    instance = next(
        item for item in plan.instances if item.instance_id == plan.controller.component
    )
    graph = json_object(decode_json(plan.graph_json))
    spec = json_object(json_object(graph["components"])[instance.instance_id])
    contracts: list[JsonObject] = [
        {
            "name": item.name,
            "input_schema": decode_json(item.input_schema_json),
            "output_schema": decode_json(item.output_schema_json),
        }
        for item in instance.operations
    ]
    bootstrap = directory / "sequence.json"
    payload: JsonObject = {"config": spec["config"], "operations": list(contracts)}
    bootstrap.write_text(encode_json(payload))
    launch = ProcessLaunch(
        Path(sys.executable), "slow_thinker_sequence", bootstrap, directory, 5, 1, 1_048_576
    )
    return ComponentProcess(launch, instance.operations)


class SequenceEnvironment:
    def __init__(self, directory: Path, plan: SequencePlan) -> None:
        self.process = sequence_process(directory, plan)
        controller = plan.controller
        host = ProcessHost(controller.component, self.process, ((controller.operation, None),))
        self.fleet = ProcessFleet((host,))
        self.agents = {
            OperationAddress(instance.instance_id, operation.name): AnswerOperation(
                instance.instance_id, operation
            )
            for instance in plan.instances
            for operation in instance.operations
            if instance.instance_id != controller.component
        }

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncGenerator[Mapping[OperationAddress, OperationPort]]:
        async with self.fleet.open(deadline) as controller:
            yield {**controller, **self.agents}

    def report(self) -> str:
        return self.fleet.report()


def configured_runtime(
    directory: Path, plan: SequencePlan
) -> tuple[RunCase, ManagedRun, SequenceEnvironment]:
    case = run_case(
        directory / "run.sqlite",
        clock=RealClock(),
        start=False,
        policy=sequence_access(plan),
        calls=100,
        revision=plan.revision,
        snapshot_json=plan.graph_json,
    )
    environment = SequenceEnvironment(directory, plan)
    finish = RunFinalization(case.authority, case.store, "run", "runtime", case.clock)
    runtime = ManagedRun(case.authority, case.service, finish, environment, case.clock() + 60, 1)
    return case, runtime, environment
