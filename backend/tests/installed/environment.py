"""Compose actual installed hosts without changing their immutable environments."""

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from slow_thinker_host import Operation, decode_json, encode_json, json_object
from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.adapters.process import (
    HostSettings,
    InstalledProcess,
    ProcessFleet,
    ProcessHost,
    ProcessSecret,
)
from slow_thinker_ii.application import OperationPort
from slow_thinker_ii.contracts import OperationContract
from slow_thinker_llm_call import effective_operation, parse_config
from slow_thinker_openai_model import ModelConfig
from slow_thinker_openai_model import effective_operation as model_operation
from support.native_model import profile
from support.openai_calls import bootstrap_record
from support.provider_process import SECRET
from support.provider_process import bootstrap_record as provider_record

from .conftest import PreparedBundle


def installed_host(
    bundle: PreparedBundle, name: str, path: Path, operation: Operation, *, provider: bool = False
) -> InstalledProcess:
    types = {
        "llm-call": "llm-call",
        "openai-model": "example.model-resource",
        "grounded-review": "example.grounded-review",
    }
    secrets = (ProcessSecret("SLOW_THINKER_SECRET_OPENAI", SECRET),) if provider else ()
    settings = HostSettings(path, path.parent, 30, 10, 1_048_576, secrets)
    contract = OperationContract(
        operation.name, encode_json(operation.input_schema), encode_json(operation.output_schema)
    )
    return InstalledProcess(
        bundle.catalog, bundle.identities[name], types[name], "0.1.0-example", settings, (contract,)
    )


class InstalledEnvironment:
    def __init__(
        self, directory: Path, bundle: PreparedBundle, name: str, provider_port: int
    ) -> None:
        self.directory, self.bundle, self.name, self.provider_port = (
            directory,
            bundle,
            name,
            provider_port,
        )
        self.gateway_port: int | None = None
        self.processes: tuple[InstalledProcess, ...] = ()
        self._fleet: ProcessFleet | None = None

    def _agent(self) -> InstalledProcess:
        assert self.gateway_port is not None
        record = bootstrap_record(f"http://127.0.0.1:{self.gateway_port}/v1")
        if self.name == "grounded-review":
            root = Path(__file__).resolve().parents[3]
            record["config"] = json_object(
                decode_json(
                    (root / "docs/contracts/examples/grounded-review.instance.json").read_text()
                )
            )["config"]
        operation = effective_operation(parse_config(record["config"]))
        record["operations"] = [
            {
                "name": operation.name,
                "input_schema": operation.input_schema,
                "output_schema": operation.output_schema,
            }
        ]
        path = self.directory / "agent.json"
        path.write_text(encode_json(record))
        return installed_host(self.bundle, self.name, path, operation)

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncGenerator[Mapping[OperationAddress, OperationPort]]:
        model_config = ModelConfig("bound-model", "gpt-6-luna", 8, 32)
        operation = model_operation(model_config)
        path = self.directory / "model.json"
        path.write_text(encode_json(provider_record(model_config, operation, self.provider_port)))
        model = installed_host(self.bundle, "openai-model", path, operation, provider=True)
        agent = self._agent()
        self.processes = (agent, model)
        self._fleet = ProcessFleet(
            (
                ProcessHost("proposer", agent, (("generate", None),)),
                ProcessHost("model", model, (("complete", OpenAIPricePolicy(profile())),)),
            )
        )
        async with self._fleet.open(deadline) as operations:
            yield operations

    def report(self) -> str:
        return "{}" if self._fleet is None else self._fleet.report()
