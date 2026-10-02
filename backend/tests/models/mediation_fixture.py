"""Real hosted transport/policy behind public operation ports and managed authority."""

from dataclasses import dataclass, replace
from pathlib import Path

import httpx2
from slow_thinker_host import Invocation
from slow_thinker_ii.access import AccessPolicy, InvocationLease, OperationAddress, Permission
from slow_thinker_ii.adapters.models import ModelPricePolicy
from slow_thinker_ii.application import (
    ManagedCalls,
    ModelBinding,
    NativeModelGateway,
    OperationReply,
    PreparedOperation,
)
from slow_thinker_ii.contracts import (
    JsonObject,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_model_provider import (
    ModelProviderHost,
    ProviderEndpoint,
    ProviderTransport,
    effective_operation,
    parse_config,
)
from support.authority import PROPOSER, REVIEWER
from support.managed_calls import RealClock
from support.native_model import response
from support.run_admission import RunCase, run_case

from .fixtures import native_response, profile

OPENAI = OperationAddress("openai-model", "complete")
DEEPSEEK = OperationAddress("deepseek-model", "complete")


class HostedModel:
    def __init__(self, provider: str) -> None:
        selected = replace(profile(provider), model_alias=provider)
        self.pricing = ModelPricePolicy(selected)
        self.native_requests: list[JsonObject] = []
        self.invocations: list[Invocation] = []
        self.status = 200
        self.body: JsonObject = response() if provider == "openai" else native_response()
        record: JsonObject = {
            "provider": provider,
            "model": selected.revision.tariff.model,
            "model_alias": provider,
            "default_output_tokens": 8,
            "maximum_output_tokens": 32,
            "reasoning_efforts": ["none"]
            if provider == "openai"
            else ["none", "low", "high", "max"],
        }
        settings = parse_config(record)
        endpoint = ProviderEndpoint(
            provider,
            "https://api.openai.com/v1" if provider == "openai" else "https://api.deepseek.com",
            "synthetic-key",
        )
        self.host = ModelProviderHost(
            settings,
            effective_operation(settings),
            ProviderTransport(endpoint, httpx2.MockTransport(self.handle)),
        )

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.native_requests.append(json_object(decode_json(request.content.decode())))
        assert request.headers["authorization"] == "Bearer synthetic-key"
        return httpx2.Response(
            self.status, json=self.body, headers={"x-request-id": "req-bound-model"}
        )

    def prepare(self, arguments_json: str) -> PreparedOperation:
        return PreparedOperation(arguments_json, self.pricing.quote(arguments_json))

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        context = Invocation(grant, deadline)
        self.invocations.append(context)
        reply = await self.host.invoke(
            "complete", json_object(decode_json(arguments_json)), context
        )
        result = OperationResult(encode_json(reply.value), reply.is_error)
        return OperationReply(result, self.pricing.reconcile(result))


@dataclass(frozen=True)
class ModelCase:
    run: RunCase
    parent: InvocationLease
    calls: ManagedCalls
    gateway: NativeModelGateway
    openai: HostedModel
    deepseek: HostedModel
    deepseek_parent: InvocationLease


def model_case(
    directory: Path,
    *,
    permitted: bool = True,
    cap: int = 1_000_000_000,
    separate_agents: bool = False,
) -> ModelCase:
    caller = "reviewer" if separate_agents else "proposer"
    permissions = (
        (Permission("proposer", OPENAI), Permission(caller, DEEPSEEK)) if permitted else ()
    )
    policy = AccessPolicy((PROPOSER, REVIEWER, OPENAI, DEEPSEEK), permissions, (PROPOSER, REVIEWER))
    run = run_case(directory / "models.sqlite", clock=RealClock(), policy=policy, limit=1_048_576)
    with run.database.transaction() as db:
        db.execute("UPDATE budget_scopes SET cap=?", (cap,))
    parent = dispatched_parent(run, PROPOSER)
    second = dispatched_parent(run, REVIEWER) if separate_agents else parent
    openai, deepseek = HostedModel("openai"), HostedModel("deepseek")
    calls = ManagedCalls(run.authority, run.service, {OPENAI: openai, DEEPSEEK: deepseek})
    gateway = NativeModelGateway(
        run.authority,
        calls,
        (
            ModelBinding("proposer", "openai", OPENAI),
            ModelBinding(caller, "deepseek", DEEPSEEK),
        ),
    )
    return ModelCase(run, parent, calls, gateway, openai, deepseek, second)


def dispatched_parent(run: RunCase, address: OperationAddress) -> InvocationLease:
    parent = run.authority.schedule(address, node_id="two-provider-node")
    run.service.reserve(parent.token, "{}", None)
    run.service.authorize(parent.token)
    return parent
