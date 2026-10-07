"""The validated journeys end to end: hosts call the gateway, events, results and totals."""

from slow_thinker_ii.accounting import Usage, charge, format_usd, input_bound, reservation_bound
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from support.configuration import llm_models
from support.examples import FLASH, J1, J2, J3, LUNA
from support.platform import Platform
from support.providers import reply

STORY = "A cat tried to learn to fly."
PROMPT = "Rewrite this story so that it is funny. Keep it under 80 words."


async def test_one_agent_runs_through_the_platform() -> None:
    platform = Platform()
    run_id = await platform.started(J1)
    record = await platform.finish(run_id)
    assert (record.status, record.reason, record.detail) == ("completed", None, "")
    kinds = platform.run_store.kinds(run_id)
    assert kinds[:4] == ["run.started", "host.ready", "run.running", "activation.started"]
    assert kinds[-1] == "run.finished"
    assert kinds.count("llm.called") == 1
    view = platform.runs.run(run_id)
    payload = f"Simulated reply to: {STORY}"
    assert [(item["node_id"], item["name"], item["payload"]) for item in view.results] == [
        ("result", "Funny story", payload)
    ]
    assert dict(view.activations_by_node) == {"story": 1, "proposer": 1, "result": 1}
    assert dict(view.messages_by_connection) == {
        "story.out -> proposer.in": 1,
        "proposer.out -> result.in": 1,
    }
    assert platform.launcher.closed == [run_id]
    assert platform.grants.active(run_id) == 0


MESSAGES: list[JsonValue] = [
    {"role": "system", "content": PROMPT},
    {"role": "user", "content": STORY},
]
REQUEST: JsonObject = {"model": LUNA, "messages": MESSAGES, "max_completion_tokens": 300}


async def test_the_model_call_is_recorded_with_its_request_and_rates() -> None:
    platform = Platform()
    run_id = await platform.started(J1)
    record = await platform.finish(run_id)
    call = platform.run_store.of(run_id, "llm.called")[0]
    assert (call.node_id, call.activation_id, call.evidence) == ("proposer", "a2", "observed")
    sent = platform.provider.requests[0]
    assert (sent.llm, sent.request, sent.timeout_s) == (LUNA, REQUEST, 300.0)
    data = call.data
    assert data["request"] == REQUEST
    assert (data["llm"], data["provider_model"], data["status"]) == (LUNA, "gpt-6-luna", 200)
    assert data["response"] is not None and data["estimated"] is False
    rates = {"input": "0.1", "cached_input": "0.01", "cache_write": "0.125", "output": "0.5"}
    assert data["rates"] == rates
    tokens = data["usage"]
    assert isinstance(tokens, dict) and record.totals is not None
    assert record.totals["llm_calls"] == 1
    assert record.totals["cost_usd"] == data["cost_usd"]
    assert record.totals["input_tokens"] == tokens["input"]
    assert record.totals["output_tokens"] == tokens["output"]


async def test_the_model_call_is_reserved_then_settled_with_its_usage() -> None:
    platform = Platform()
    run_id = await platform.started(J1)
    await platform.finish(run_id)
    data = platform.run_store.of(run_id, "llm.called")[0].data
    tariff = llm_models()[0].tariff
    reserved = reservation_bound(tariff, input_bound(len(encode_json(MESSAGES).encode()), 2), 300)
    assert data["reserved_usd"] == format_usd(reserved)
    assert platform.ledger.unsettled() == []
    row = next(iter(platform.ledger.rows.values()))
    assert (row.run_id, row.reserved, row.estimated) == (run_id, reserved, False)
    assert row.charge is not None and 0 < row.charge < reserved
    assert format_usd(row.charge) == data["cost_usd"]
    tokens = data["usage"]
    assert isinstance(tokens, dict)
    now = platform.clock.now()
    assert charge(tariff, _usage(tokens), now, now)[0] == row.charge


async def test_an_embedded_router_selects_the_result() -> None:
    platform = Platform(steps={FLASH: [reply('{"score": 8}')]})
    run_id = await platform.started(J2)
    record = await platform.finish(run_id)
    assert record.status == "completed"
    results = platform.runs.run(run_id).results
    assert [(item["node_id"], item["payload"]) for item in results] == [("funny", STORY)]
    sent = platform.provider.requests[0].request
    assert (sent["reasoning_effort"], sent["temperature"], sent["max_completion_tokens"]) == (
        "none",
        0.2,
        50,
    )
    response_format = sent["response_format"]
    assert isinstance(response_format, dict) and response_format["type"] == "json_schema"
    routed = platform.run_store.of(run_id, "component.called")[1]
    assert routed.data["result"] == {"port": "funny", "payload": STORY}


async def test_the_review_loop_is_accepted_at_the_second_review() -> None:
    platform = Platform(steps={FLASH: [reply('{"score": 5}'), reply('{"score": 8}')]})
    record = await platform.completed(J3)
    assert record.status == "completed"
    assert record.totals is not None
    totals = (record.totals["activations"], record.totals["messages"], record.totals["llm_calls"])
    assert totals == (6, 5, 4)


async def test_the_review_loop_stops_at_the_activation_limit() -> None:
    platform = Platform(steps={FLASH: [reply('{"score": 6}')]})
    run_id = await platform.started(J3)
    record = await platform.finish(run_id)
    assert (record.status, record.reason) == ("stopped", "activation_limit")
    assert (
        record.detail == "The run reached its limit of 10 activations before Reviewer could start."
    )
    assert record.totals is not None
    totals = (record.totals["activations"], record.totals["messages"], record.totals["llm_calls"])
    assert totals == (10, 10, 9)
    finished = platform.run_store.of(run_id, "run.finished")[0]
    assert finished.data["dropped"] == 1
    assert platform.runs.run(run_id).results == ()


def _usage(tokens: JsonObject) -> Usage:
    names = ("input", "cached_input", "cache_write", "output")
    counts = [count for count in (tokens[name] for name in names) if isinstance(count, int)]
    assert len(counts) == len(names)
    return Usage(*counts)
