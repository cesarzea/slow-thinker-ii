"""Two independent managed processes exercise the entire agent-to-provider path."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessFleet, ProcessHost
from slow_thinker_ii.application import OperationPort

from .llm_process import llm_process
from .native_model import profile
from .provider_process import provider_process


class ProviderEnvironment:
    def __init__(self, directory: Path, provider_port: int) -> None:
        self.directory, self.provider_port = directory, provider_port
        self.gateway_port: int | None = None
        self.processes: tuple[ComponentProcess, ...] = ()
        self._fleet: ProcessFleet | None = None

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        assert self.gateway_port is not None
        agent = llm_process(self.directory, self.gateway_port)
        provider = provider_process(self.directory, self.provider_port)
        self.processes = (agent, provider)
        self._fleet = ProcessFleet(
            (
                ProcessHost("proposer", agent, (("generate", None),)),
                ProcessHost("model", provider, (("complete", OpenAIPricePolicy(profile())),)),
            )
        )
        async with self._fleet.open(deadline) as operations:
            yield operations

    def report(self) -> str:
        return "{}" if self._fleet is None else self._fleet.report()
