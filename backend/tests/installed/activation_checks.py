"""Actual sequence inputs must match the retained source references of each activation."""

import httpx
from slow_thinker_ii.contracts import JsonObject, json_object
from slow_thinker_ii.definitions import read_pointer
from support.operator_http import payload
from support.operator_trace import objects


async def inspect_activations(
    client: httpx.AsyncClient, base: str, calls: list[JsonObject]
) -> None:
    roots = [
        call
        for call in calls
        if json_object(call["context"])["activation_id"] is not None
        and json_object(call["context"])["parent_call_id"] is None
    ]
    identities: set[str] = set()
    for root in roots:
        identity = str(json_object(root["context"])["activation_id"])
        assert identity not in identities
        identities.add(identity)
        response = await client.get(f"{base}/activations/{identity}")
        assert response.status_code == 200
        activation = payload(response)
        check_activation(activation, root, calls, identity)
        await inspect_bindings(client, base, activation)


async def inspect_bindings(client: httpx.AsyncClient, base: str, activation: JsonObject) -> None:
    bindings = payload(await client.get(f"{base}/payloads/{activation['bindings_payload_id']}"))
    content = json_object(bindings["content"])
    assert content["status"] == "present" and content["source"] == "admitted_definition"
    request = payload(await client.get(f"{base}/payloads/{activation['input_payload_id']}"))
    effective = json_object(request["content"])
    for name, value in json_object(content["inputs"]).items():
        reference = json_object(value)
        declaration = json_object(reference["declaration"])
        if reference["status"] == "literal":
            assert effective[name] == declaration["value"]
        else:
            assert reference["status"] == "resolved"
            original = payload(await client.get(f"{base}/payloads/{reference['payload_id']}"))
            pointer = declaration["pointer"]
            assert isinstance(pointer, str)
            assert effective[name] == read_pointer(original["content"], pointer)


def check_activation(
    activation: JsonObject, root: JsonObject, calls: list[JsonObject], identity: str
) -> None:
    assert activation["root_call_id"] == root["call_id"]
    assert activation["state"] == root["state"]
    expected = {
        str(call["call_id"])
        for call in calls
        if json_object(call["context"])["activation_id"] == identity
    }
    assert {
        str(item["call_id"]) for item in objects(json_object(activation["calls"])["items"])
    } == expected
    if root["state"] == "completed":
        assert activation["output_payload_id"] == "response:" + str(root["result_receipt_id"])
    else:
        assert activation["output_payload_id"] is None
