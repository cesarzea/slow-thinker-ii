"""Activation reads separate repeated participants and preserve successful output eligibility."""

import pytest
from slow_thinker_ii.contracts import json_object
from support.activation_trace import repeated_trace
from support.operator_http import HttpCase, payload
from support.operator_trace import completed_trace, objects


async def test_repeated_participant_has_distinct_effective_inputs_and_activation_ids(
    api: HttpCase,
) -> None:
    run, calls = await repeated_trace(api)
    identities = [str(json_object(call["context"])["activation_id"]) for call in calls]
    assert len(set(identities)) == 2
    first = payload(await api.client.get(f"/api/v1/runs/{run}/activations/{identities[0]}"))
    second = payload(await api.client.get(f"/api/v1/runs/{run}/activations/{identities[1]}"))
    assert first["target"] == second["target"] == {"instance": "worker", "operation": "run"}
    assert first["node_id"] == "first" and second["node_id"] == "second"
    assert len(objects(json_object(first["calls"])["items"])) == 1
    args = payload(
        await api.client.get(f"/api/v1/runs/{run}/payloads/{second['input_payload_id']}")
    )
    assert args["content"] == {"previous": True}
    output = payload(
        await api.client.get(f"/api/v1/runs/{run}/payloads/{second['output_payload_id']}")
    )
    assert output["content"] == {"done": True}


async def test_binding_sources_link_frozen_input_and_earlier_published_output(
    api: HttpCase,
) -> None:
    run, calls = await repeated_trace(api)
    base = f"/api/v1/runs/{run}/payloads/"
    first = json_object(
        payload(await api.client.get(base + "bindings:" + str(calls[0]["call_id"])))["content"]
    )
    second = json_object(
        payload(await api.client.get(base + "bindings:" + str(calls[1]["call_id"])))["content"]
    )
    origin = json_object(json_object(first["inputs"])["p"])
    assert origin["payload_id"] == "run-input:" + run
    source = json_object(json_object(second["inputs"])["previous"])
    assert source["status"] == "resolved" and source["call_id"] == calls[0]["call_id"]
    assert json_object(source["declaration"])["pointer"] == "/done"
    assert payload(await api.client.get(base + str(origin["payload_id"])))["content"] == {
        "p": "test"
    }
    assert payload(await api.client.get(base + str(source["payload_id"])))["content"] == {
        "done": True
    }


async def test_activation_and_binding_references_cannot_cross_runs(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    details = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
    activation = json_object(details["context"])["activation_id"]
    other, _ = await completed_trace(api, "another")
    for path in (
        f"activations/{activation}",
        f"payloads/bindings:{call}",
        f"payloads/run-input:{run}",
    ):
        assert (await api.client.get(f"/api/v1/runs/{other}/{path}")).status_code == 404
    assert (await api.client.get(f"/api/v1/runs/{run}/activations/missing")).status_code == 404


@pytest.mark.parametrize("query", ["cursor=bad", "cursor=a&cursor=b", "limit=9999"])
async def test_activation_paging_rejects_invalid_parameters(api: HttpCase, query: str) -> None:
    run, calls = await repeated_trace(api)
    activation = json_object(calls[0]["context"])["activation_id"]
    assert (
        await api.client.get(f"/api/v1/runs/{run}/activations/{activation}?{query}")
    ).status_code == 400


async def test_missing_definition_does_not_manufacture_binding_provenance(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    content = payload(await api.client.get(f"/api/v1/runs/{run}/payloads/bindings:{call}"))
    assert content["content"] == {"status": "unavailable", "reason": "definition_not_recorded"}


async def test_multiple_prior_activations_are_not_guessed_as_the_binding_source(
    api: HttpCase,
) -> None:
    run, calls = await repeated_trace(api, repeat_first=True)
    response = await api.client.get(f"/api/v1/runs/{run}/payloads/bindings:{calls[-1]['call_id']}")
    bindings = json_object(payload(response)["content"])
    source = json_object(json_object(bindings["inputs"])["previous"])
    assert source["status"] == "unavailable" and source["reason"] == "source_not_unambiguous"
    assert "call_id" not in source and "payload_id" not in source
