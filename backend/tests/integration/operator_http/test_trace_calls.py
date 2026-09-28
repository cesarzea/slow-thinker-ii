"""Call evidence keeps causal links, receipt eligibility and leaf costs separate."""

import time

from slow_thinker_ii.access import InvocationEnd
from slow_thinker_ii.application import CallReceipt, ChargeBasis, ChargeEvidence
from slow_thinker_ii.contracts import json_object
from support.coordinator import eventually
from support.operator_http import HttpCase, payload
from support.operator_trace import completed_trace, event_items, objects


async def test_call_details_expose_actual_arguments_responses_and_own_cost(api: HttpCase) -> None:
    api.case.preparer.operation.charge = ChargeBasis(7, "tariff", '{"basis":"fixture"}')
    api.case.preparer.operation.evidence = ChargeEvidence('{"tokens":2}', 3, "fixture")
    run, call = await completed_trace(api)
    base = f"/api/v1/runs/{run}"
    details = payload(await api.client.get(f"{base}/calls/{call}"))
    context = json_object(details["context"])
    assert context["parent_call_id"] is None
    assert context["target"] == {"instance": "worker", "operation": "run"}
    cost = json_object(details["accounting"])
    assert cost["amount"] == "0.000000003" and cost["outstanding"] == "0.000000000"
    receipts = objects(json_object(details["receipts"])["items"])
    assert receipts[0]["publish"] is True and receipts[0]["source"] == "fixture"
    request = payload(await api.client.get(f"{base}/payloads/{details['request_payload_id']}"))
    response = payload(
        await api.client.get(f"{base}/payloads/{receipts[0]['response_payload_id']}")
    )
    usage = payload(await api.client.get(f"{base}/payloads/{receipts[0]['usage_payload_id']}"))
    pricing = payload(await api.client.get(f"{base}/payloads/{details['pricing_payload_id']}"))
    assert request["content"] == {} and response["content"] == {"done": True}
    assert usage["content"] == {"tokens": 2} and pricing["content"] == {"basis": "fixture"}


async def test_late_receipts_are_inspectable_without_republishing_the_output(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    path = f"/api/v1/runs/{run}/calls/{call}"
    for index in range(3):
        with api.case.runs.begin() as transaction:
            transaction.receive(
                CallReceipt(f"late{index}", call, "null", True),
                InvocationEnd(call, False, "late", ()),
                time.monotonic(),
                transaction.run(run).runtime_id,
            )
    first = payload(await api.client.get(path))
    receipts = json_object(first["receipts"])
    cursor = receipts["next_cursor"]
    assert isinstance(cursor, str) and len(objects(receipts["items"])) == 2
    next_page = payload(await api.client.get(path, params={"cursor": cursor}))
    late = objects(json_object(next_page["receipts"])["items"])
    assert len(late) == 2 and all(item["publish"] is False for item in late)
    response = payload(await api.client.get(f"/api/v1/runs/{run}/payloads/response:late1"))
    assert response["status"] == "present" and response["content"] is None
    assert response["size_bytes"] == 4
    assert first["result_receipt_id"] == next_page["result_receipt_id"]


async def test_call_and_receipt_payloads_cannot_cross_run_boundaries(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    details = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    receipt = objects(json_object(details["receipts"])["items"])[0]
    other, _ = await completed_trace(api, "second")
    for suffix in (
        f"calls/{call}",
        f"payloads/request:{call}",
        f"payloads/{receipt['response_payload_id']}",
    ):
        assert (await api.client.get(f"/api/v1/runs/{other}/{suffix}")).status_code == 404
    assert (await api.client.get(f"/api/v1/runs/{run}/calls/missing")).status_code == 404


async def test_missing_usage_or_price_is_explicit_without_fabricated_zero(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    details = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    assert details["accounting"] is None and details["pricing_payload_id"] is None
    receipt = objects(json_object(details["receipts"])["items"])[0]
    for identity in (str(receipt["usage_payload_id"]), "pricing:" + call):
        content = payload(await api.client.get(f"/api/v1/runs/{run}/payloads/{identity}"))
        assert content["status"] == "unavailable" and content["reason"] == "not_recorded"
        assert content["size_bytes"] is None and content["content"] is None


async def test_cancelled_call_retains_unconfirmed_attempt_cost(api: HttpCase) -> None:
    operation = api.case.preparer.operation
    operation.charge = ChargeBasis(7, "tariff", "{}")
    operation.release.clear()
    run = str(payload(await api.client.post("/api/v1/runs", json=api.start()))["target_id"])
    await operation.started.wait()
    await api.client.post(
        f"/api/v1/runs/{run}/stop", json={"schema_version": "0.1-draft", "command_id": "stop"}
    )
    await eventually(lambda: not api.case.coordinator.pending().runs)
    call = next(
        item["call_id"] for item in await event_items(api, run) if item["event"] == "call.requested"
    )
    details = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    cost = json_object(details["accounting"])
    assert cost["amount"] is None and cost["outstanding"] == "0.000000007"
    assert details["result_receipt_id"] is None
