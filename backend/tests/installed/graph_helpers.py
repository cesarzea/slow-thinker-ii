"""Local fixture profiles drive the production graph compiler and installed runtime."""

from dataclasses import replace

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.catalog import InstalledGraphCompiler, InstalledPlan
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.adapters.process import HostBinding, ProcessSecret
from slow_thinker_ii.application import ManagedResult, ManagedRun, ModelBinding
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object
from support.native_model import profile
from support.provider_process import SECRET
from support.sequence_plans import SCHEMAS, graph_value

from .conftest import PreparedBundle
from .coordinator_fixture import selected_types


class RunRouter:
    def __init__(self) -> None:
        self.runtime: ManagedRun | None = None

    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult:
        assert self.runtime is not None
        return await self.runtime.invoke(grant, alias, arguments_json)


def compile_graph(bundle: PreparedBundle, name: str) -> InstalledPlan:
    types = selected_types(bundle)
    graph = graph_value(name)
    configs: dict[str, str] = {}
    for identity, value in json_object(graph["components"]).items():
        component = json_object(value)
        if component["type_id"] == "example.model-resource":
            model = json_object(component["config"])
            configs[identity] = encode_json(
                {
                    "model_alias": model["model"],
                    "model": profile().revision.tariff.model,
                    "default_output_tokens": 8,
                    "maximum_output_tokens": 1024,
                }
            )
    return InstalledGraphCompiler(bundle.catalog, SCHEMAS, types).compile(
        encode_json(graph), '{"problem":"Design a workshop"}', configs
    )


def model_bindings(installed: InstalledPlan) -> tuple[ModelBinding, ...]:
    graph = json_object(decode_json(installed.plan.graph_json))
    components = json_object(graph["components"])
    alias = str(json_object(json_object(components["model"])["config"])["model"])
    return tuple(
        ModelBinding(identity, alias, OperationAddress("model", "complete"))
        for identity, item in components.items()
        if "model" in json_object(json_object(item)["resources"])
    )


def host_bindings(
    installed: InstalledPlan, gateway_port: int, provider_port: int
) -> dict[str, HostBinding]:
    model = next(item for item in installed.configurations if item.instance_id == "model")
    alias = str(json_object(decode_json(model.description.config_json))["model_alias"])
    bindings: dict[str, HostBinding] = {
        item.instance_id: HostBinding() for item in installed.configurations
    }
    for item in model_bindings(installed):
        client: JsonObject = {
            "openai": {
                "base_url": f"http://127.0.0.1:{gateway_port}/v1",
                "model": alias,
                "timeout_seconds": 5,
                "close_seconds": 1,
            }
        }
        bindings[item.caller] = HostBinding(encode_json(client))
    bindings["model"] = provider_binding(alias, provider_port)
    return bindings


def provider_binding(alias: str, provider_port: int) -> HostBinding:
    provider: JsonObject = {
        "provider": {
            "base_url": f"http://127.0.0.1:{provider_port}/v1",
            "timeout_seconds": 5,
            "close_seconds": 1,
            "max_response_bytes": 524_288,
        }
    }
    price = OpenAIPricePolicy(replace(profile(), model_alias=alias))
    return HostBinding(
        encode_json(provider),
        (("complete", price),),
        (ProcessSecret("SLOW_THINKER_SECRET_OPENAI", SECRET),),
    )
