"""Draft payloads contain only two exact identities; lineage remains immutable."""

import pytest
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object
from support.definition_http import PARENT, ROOT, DefinitionHttp, error_data, reference, variant


@pytest.mark.parametrize(
    "body",
    [
        {"source": PARENT},
        {"source": PARENT, "target": reference(), "extra": True},
        {"source": {**PARENT, "definition": {}}, "target": reference()},
        {"source": PARENT, "target": {**reference(), "revision": 1}},
        {"source": PARENT, "target": {"graph_id": "Bad", "revision": "x"}},
        {"source": PARENT, "target": {"graph_id": "single-agent", "revision": ""}},
        {"source": PARENT, "target": PARENT},
    ],
)
async def test_invalid_draft_identities(definitions: DefinitionHttp, body: JsonObject) -> None:
    response = await definitions.client.post(ROOT + "/draft", json=body)
    error_data(response, 422, "invalid_definition")


async def test_unknown_source_and_occupied_target(definitions: DefinitionHttp) -> None:
    response = await definitions.client.post(
        ROOT + "/draft", json={"source": reference("missing"), "target": reference()}
    )
    error_data(response, 404, "definition_not_found")
    definitions.service.save(variant())
    response = await definitions.client.post(
        ROOT + "/draft", json={"source": PARENT, "target": reference()}
    )
    assert response.status_code == 200
    assert definitions.service.definition(**reference()) == variant()


@pytest.mark.parametrize(
    "parent,code",
    [(reference("missing"), "definition_parent_missing"), (reference(), "invalid_definition")],
)
@pytest.mark.parametrize("path", [ROOT, ROOT + "/validate"])
async def test_missing_and_self_parent(
    definitions: DefinitionHttp, parent: JsonObject, code: str, path: str
) -> None:
    value = json_object(decode_json(variant()))
    value["derived_from"] = parent
    response = await definitions.client.post(
        path, content=encode_json(value), headers={"content-type": "application/json"}
    )
    error_data(response, 422, code)
