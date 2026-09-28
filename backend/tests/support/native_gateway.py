"""A durably dispatched parent supplies real invocation authority to native HTTP clients."""

from dataclasses import dataclass
from pathlib import Path

import httpx2
from openai import AsyncOpenAI
from slow_thinker_ii.access import InvocationLease
from slow_thinker_ii.application import ManagedCalls, ModelBinding, NativeModelGateway

from .authority import MODEL, PROPOSER
from .native_model import MeteredModel, model_case
from .run_admission import RunCase, outstanding


@dataclass(frozen=True)
class NativeCase:
    run: RunCase
    model: MeteredModel
    parent: InvocationLease
    calls: ManagedCalls
    gateway: NativeModelGateway


def native_case(directory: Path, cap: int = 1_000_000_000) -> NativeCase:
    case, model = model_case(directory, cap=cap), MeteredModel()
    parent = case.authority.schedule(PROPOSER, node_id="draft")
    case.service.reserve(parent.token, "{}", None)
    case.service.authorize(parent.token)
    calls = ManagedCalls(case.authority, case.service, {MODEL: model})
    gateway = NativeModelGateway(
        case.authority, calls, (ModelBinding("proposer", "bound-model", MODEL),)
    )
    return NativeCase(case, model, parent, calls, gateway)


def sdk_client(port: int, grant: str) -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=f"http://127.0.0.1:{port}/v1",
        api_key=grant,
        max_retries=0,
        http_client=httpx2.AsyncClient(trust_env=False, timeout=5),
    )


def assert_recorded(case: NativeCase) -> None:
    assert outstanding(case.run) == (0, 0, 0)
    with case.run.store.begin() as transaction:
        assert all(scope.settled == 2390 for scope in transaction.scopes(case.run.keys))
        children = [
            transaction.call(event.call_id)
            for event in transaction.events("run")
            if event.event == "call.requested"
            and event.call_id != case.parent.context.call_id
            and event.call_id
        ]
        assert (
            len(children) == 1
            and children[0].prepared.context.parent_call_id == case.parent.context.call_id
        )
        assert children[0].prepared.context.node_id == "draft"
        assert case.parent.token not in str(transaction.events("run"))
