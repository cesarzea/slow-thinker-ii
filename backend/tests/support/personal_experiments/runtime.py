"""A declared fixture runtime executes the production prepared program and permission policy."""

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

from slow_thinker_ii.access import CallAuthority, CallLimits, OperationAddress
from slow_thinker_ii.adapters.catalog import SequenceCompiler
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.adapters.sqlite import SqliteRunStore
from slow_thinker_ii.application import (
    ManagedRun,
    NativeModelGateway,
    OperationPort,
    PreparedWorkflow,
    RunAdmission,
    RunFinalization,
    RunRecord,
)
from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ..managed_calls import RealClock
from ..native_model import MeteredModel
from ..sequence_plans import SCHEMAS, resolved
from ..sequence_runtime import SequenceEnvironment
from .native_transport import NativeSDKTransport, PreparedLLMOperation


class PreparedFixtureEnvironment:
    def __init__(self, directory: Path, workflow: PreparedWorkflow) -> None:
        snapshot = json_object(decode_json(workflow.start.snapshot_json))
        definition = json_object(snapshot["definition"])
        plan = SequenceCompiler(SCHEMAS).compile(
            encode_json(definition), encode_json(snapshot["input"]), resolved(definition)
        )
        self.sequence = SequenceEnvironment(directory, plan)
        config = json_object(json_object(json_object(snapshot["instances"])["proposer"])["config"])
        self.transport = NativeSDKTransport()
        binding = workflow.models[0]
        self.agent = PreparedLLMOperation(config, binding.model_alias, self.transport)
        self.model = MeteredModel()
        self.model.profile = replace(
            self.model.profile, model_alias=binding.model_alias, maximum_output_tokens=8
        )
        self.model.pricing = OpenAIPricePolicy(self.model.profile)
        self.target = binding.target

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncGenerator[Mapping[OperationAddress, OperationPort]]:
        async with self.sequence.open(deadline) as operations:
            yield {
                **operations,
                OperationAddress("proposer", "generate"): self.agent,
                self.target: self.model,
            }

    def report(self) -> str:
        return self.sequence.report()


def prepared_runtime(
    workflow: PreparedWorkflow,
    record: RunRecord,
    store: SqliteRunStore,
    environment: PreparedFixtureEnvironment,
    clock: RealClock,
) -> ManagedRun:
    limits = workflow.start.configuration.limits
    authority = CallAuthority(
        record.run_id,
        record.graph_revision,
        workflow.policy,
        CallLimits(limits.max_calls, limits.max_depth, limits.call_seconds),
        record.deadline,
        clock,
    )
    admission = RunAdmission(authority, store, record.run_id, record.runtime_id, clock)
    finish = RunFinalization(authority, store, record.run_id, record.runtime_id, clock)
    runtime = ManagedRun(
        authority, admission, finish, environment, record.deadline, limits.shutdown_seconds
    )
    environment.transport.gateway = NativeModelGateway(authority, runtime, workflow.models)
    return runtime
