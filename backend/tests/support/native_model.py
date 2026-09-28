"""A metered model fixture uses the real request policy, tariff and accounting evidence."""

from collections.abc import Callable
from pathlib import Path

from slow_thinker_ii.access import AccessPolicy, Permission
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy, OpenAIProfile
from slow_thinker_ii.adapters.tariffs import parse_catalog
from slow_thinker_ii.application import OperationReply, PreparedOperation
from slow_thinker_ii.contracts import JsonObject, OperationResult, encode_json

from .authority import MODEL, PROPOSER
from .catalog import PAYLOAD
from .managed_calls import RealClock
from .openai_calls import completion
from .run_admission import RunCase, run_case


def profile() -> OpenAIProfile:
    revision = parse_catalog(PAYLOAD, 1)
    return OpenAIProfile(revision, "bound-model", 8, 32, (revision.tariff.model,))


def response() -> JsonObject:
    result: JsonObject = completion("success")
    result.update(
        {"model": "gpt-6-luna", "service_tier": "default", "future_field": {"kept": True}}
    )
    result["usage"] = {
        "prompt_tokens": 12,
        "completion_tokens": 3,
        "total_tokens": 15,
        "prompt_tokens_details": {"cached_tokens": 4, "cache_write_tokens": 2},
    }
    return result


class MeteredModel:
    def __init__(self) -> None:
        self.profile = profile()
        self.pricing = OpenAIPricePolicy(self.profile)
        self.result = OperationResult(
            encode_json({"response": response(), "request_id": "req_fixture"}), False
        )
        self.calls: list[JsonObject] = []
        self.before_reply: Callable[[], None] | None = None

    def prepare(self, arguments_json: str) -> PreparedOperation:
        return PreparedOperation(arguments_json, self.pricing.quote(arguments_json))

    async def invoke(self, arguments_json: str, grant: str, deadline: float) -> OperationReply:
        del grant, deadline
        self.calls.append(self.profile.request(arguments_json))
        if self.before_reply is not None:
            self.before_reply()
        return OperationReply(self.result, self.pricing.reconcile(self.result))


def model_case(directory: Path, *, start: bool = True, cap: int = 1_000_000_000) -> RunCase:
    policy = AccessPolicy((PROPOSER, MODEL), (Permission("proposer", MODEL),), (PROPOSER,))
    case = run_case(
        directory / "run.sqlite", clock=RealClock(), start=start, policy=policy, limit=1_048_576
    )
    with case.database.transaction() as connection:
        connection.execute("UPDATE budget_scopes SET cap=?", (cap,))
    return case
