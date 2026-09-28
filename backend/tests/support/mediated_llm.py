"""The actual LLMCall process reaches a fixture model only through the platform gateway."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessOperation
from slow_thinker_ii.application import ManagedCalls, OperationPort

from .authority import MODEL, PROPOSER
from .llm_process import llm_process
from .native_model import MeteredModel


class MediatedEnvironment:
    def __init__(self, directory: Path, model: MeteredModel) -> None:
        self.directory, self.model = directory, model
        self.port: int | None = None
        self.process: ComponentProcess | None = None

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        del deadline
        assert self.port is not None
        self.process = llm_process(self.directory, self.port)
        async with self.process.connect() as connection:
            yield {PROPOSER: ProcessOperation(connection, "generate", None), MODEL: self.model}

    def report(self) -> str:
        return "{}"


class GenerateProgram:
    async def execute(self, calls: ManagedCalls) -> str:
        result = await calls.schedule(PROPOSER, '{"question":"test"}', node_id="draft")
        if not result.outcome.publish:
            raise ValueError("Agent did not produce an eligible result")
        return result.result.payload_json
