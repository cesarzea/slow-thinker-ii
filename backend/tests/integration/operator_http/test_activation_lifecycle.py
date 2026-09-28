"""Activation reads do not turn failures into outputs or mix paging windows."""

from slow_thinker_ii.contracts import OperationResult, json_object
from support.activation_rows import add_related_call
from support.operator_http import HttpCase, payload
from support.operator_trace import completed_trace, event_items, objects


async def test_failed_activation_retains_response_without_publishing_it_as_output(
    api: HttpCase,
) -> None:
    api.case.preparer.operation.result = OperationResult('{"error":"fixture"}', True)
    run, call = await completed_trace(api)
    detail = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    identity = json_object(detail["context"])["activation_id"]
    response = await api.client.get(f"/api/v1/runs/{run}/activations/{identity}")
    assert payload(response)["state"] == "failed" and payload(response)["output_payload_id"] is None
    assert detail["result_receipt_id"] is not None


async def test_activation_page_excludes_calls_added_after_initial_boundary(api: HttpCase) -> None:
    operation = api.case.preparer.operation
    operation.release.clear()
    run = str(payload(await api.client.post("/api/v1/runs", json=api.start()))["target_id"])
    await operation.started.wait()
    call = str(
        next(
            item["call_id"]
            for item in await event_items(api, run)
            if item["event"] == "call.requested"
        )
    )
    detail = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    activation = json_object(detail["context"])["activation_id"]
    for child in ("child1", "child2"):
        add_related_call(api, call, child)
    path = f"/api/v1/runs/{run}/activations/{activation}"
    first = payload(await api.client.get(path))
    assert first["output_payload_id"] is None
    cursor = json_object(first["calls"])["next_cursor"]
    assert isinstance(cursor, str)
    add_related_call(api, call, "later")
    second = payload(await api.client.get(path, params={"cursor": cursor}))
    items = objects(json_object(second["calls"])["items"])
    assert [item["call_id"] for item in items] == ["child2"]
    assert json_object(second["calls"])["next_cursor"] is None
    foreign = await api.client.get(f"/api/v1/runs/{run}/calls/{call}", params={"cursor": cursor})
    assert foreign.status_code == 400


async def test_ambiguous_activation_roots_fail_instead_of_selecting_a_participant(
    api: HttpCase,
) -> None:
    run, call = await completed_trace(api)
    detail = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    activation = json_object(detail["context"])["activation_id"]
    add_related_call(api, call, "duplicate-root", child=False)
    response = await api.client.get(f"/api/v1/runs/{run}/activations/{activation}")
    assert response.status_code == 503
    assert "originating call" not in response.text


async def test_activation_inspection_requires_operator_authentication(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    detail = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    activation = json_object(detail["context"])["activation_id"]
    response = await api.client.get(
        f"/api/v1/runs/{run}/activations/{activation}", headers={"authorization": ""}
    )
    assert response.status_code == 401
