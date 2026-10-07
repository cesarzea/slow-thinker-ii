"""The simulated provider behind the application's LLM gateway, as browser journeys use it."""

from collections.abc import Mapping, Sequence

from slow_thinker_ii.adapters.providers import SimulatedProvider
from slow_thinker_ii.application import LlmGateway, RunRecord
from slow_thinker_ii.contracts import JsonObject, json_object
from slow_thinker_ii.graphs import RunPlan
from support.components import ComponentHosts
from support.configuration import llm_models
from support.examples import FLASH, J3
from support.platform import Platform

STORY = "Simulated reply to: A cat tried to learn to fly."


async def review(replies: Mapping[str, Sequence[str]] | None) -> tuple[Platform, RunRecord]:
    """Runs J3 with component hosts calling a gateway over `SimulatedProvider(replies)`."""
    gateways: list[LlmGateway] = []  # the gateway needs the platform's run service

    def hosts(plan: RunPlan) -> ComponentHosts:
        return ComponentHosts(plan, lambda: gateways[0])

    platform = Platform(hosts=hosts)
    provider = SimulatedProvider(replies)
    budgets, clock = platform.budgets, platform.clock
    gateways.append(
        LlmGateway(
            runs=platform.runs,
            ledger=platform.ledger,
            provider=provider,
            models=llm_models(),
            budgets=budgets,
            clock=clock,
        )
    )
    record = await platform.completed(J3)
    assert not platform.provider.requests  # every call went through the simulated provider
    return platform, record


def reviewer_calls(platform: Platform, record: RunRecord) -> list[JsonObject]:
    events = platform.run_store.of(record.run_id, "llm.called")
    return [event.data for event in events if event.node_id == "reviewer"]


def answered(call: JsonObject) -> str:
    response = json_object(call["response"])
    choices = response["choices"]
    assert isinstance(choices, list)
    return str(json_object(json_object(choices[0])["message"])["content"])


async def test_the_schema_instance_accepts_the_first_review() -> None:
    platform, record = await review(None)
    assert (record.status, record.reason) == ("completed", None)
    [call] = reviewer_calls(platform, record)
    request = json_object(call["request"])
    assert json_object(request["response_format"])["type"] == "json_schema"
    assert answered(call) == '{"score":10}'
    assert (call["status"], call["estimated"], call["provider_model"]) == (
        200,
        False,
        "deepseek-flash",
    )
    results = platform.runs.run(record.run_id).results
    assert [item["payload"] for item in results] == [STORY]


async def test_scripted_reviews_cycle_through_the_loop() -> None:
    platform, record = await review({FLASH: ('{"score": 5}', '{"score": 8}')})
    assert (record.status, record.reason) == ("completed", None)
    calls = reviewer_calls(platform, record)
    assert [answered(call) for call in calls] == ['{"score": 5}', '{"score": 8}']
    assert all(call["usage"] is not None and call["estimated"] is False for call in calls)
    results = platform.runs.run(record.run_id).results
    assert [item["payload"] for item in results] == [f"Simulated reply to: {STORY}"]
