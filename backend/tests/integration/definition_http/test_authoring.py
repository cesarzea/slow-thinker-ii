"""Immutable HTTP authoring retains exact source values, identity and lineage."""

import asyncio

import pytest
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.definition_http import PARENT, ROOT, DefinitionHttp, error_data, reference, variant


async def test_validate_save_replay_and_exact_numeric_source(definitions: DefinitionHttp) -> None:
    source = variant()
    headers = {"content-type": "application/json"}
    validation = await definitions.client.post(ROOT + "/validate", content=source, headers=headers)
    assert validation.status_code == 200
    assert validation.json() == {**reference(), "validation_scope": "definition"}
    saved = await definitions.client.post(ROOT, content=source, headers=headers)
    assert saved.status_code == 201 and saved.json() == {**reference(), "created": True}
    loaded = await definitions.client.get(ROOT + "/source", params=reference())
    assert loaded.status_code == 200 and loaded.text == source
    assert loaded.headers["content-type"] == "application/json"
    assert loaded.headers["cache-control"] == "no-store" and "view_token" not in loaded.text
    replay = await definitions.client.post(ROOT, content=loaded.text, headers=headers)
    assert replay.status_code == 200 and replay.json()["created"] is False
    detail = await definitions.client.get(ROOT + "/detail", params=reference())
    assert detail.json()["definition"]["extensions"]["fixture:integer"] == 9007199254740993
    assert '"fixture:float":1.0' in loaded.text


async def test_concurrent_saves_insert_one_revision(definitions: DefinitionHttp) -> None:
    replies = await asyncio.gather(
        *(
            definitions.client.post(
                ROOT, content=variant(), headers={"content-type": "application/json"}
            )
            for _ in range(2)
        )
    )
    assert sorted(reply.status_code for reply in replies) == [200, 201]
    assert sum(reply.json()["created"] for reply in replies) == 1
    personals = [item for item in definitions.service.page(100).items if item.origin == "personal"]
    assert len(personals) == 1


async def test_personal_and_bundled_collisions_never_replace(definitions: DefinitionHttp) -> None:
    source = variant()
    definitions.service.save(source)
    changed = json_object(decode_json(source))
    changed["extensions"] = {"fixture:changed": True}
    response = await definitions.client.post(
        ROOT, content=encode_json(changed), headers={"content-type": "application/json"}
    )
    error_data(response, 409, "definition_conflict")
    assert definitions.service.definition(**reference()) == source
    changed["revision"] = PARENT["revision"]
    del changed["derived_from"]
    response = await definitions.client.post(
        ROOT, content=encode_json(changed), headers={"content-type": "application/json"}
    )
    error_data(response, 409, "definition_conflict")
    bundled = definitions.service.definition(**PARENT)
    assert json_object(decode_json(bundled)).get("extensions") is None
    replay = await definitions.client.post(
        ROOT, content=bundled, headers={"content-type": "application/json"}
    )
    assert replay.status_code == 200 and replay.json()["created"] is False


async def test_draft_is_unsaved_and_preserves_numeric_values(definitions: DefinitionHttp) -> None:
    definitions.service.save(variant())
    target = reference("variant β / second")
    draft = await definitions.client.post(
        ROOT + "/draft", json={"source": reference(), "target": target}
    )
    assert draft.status_code == 200 and '"fixture:float":1.0' in draft.text
    value = json_object(decode_json(draft.text))
    assert value["derived_from"] == reference()
    assert value["revision"] == target["revision"] and "view_token" not in value
    assert json_object(value["extensions"])["fixture:integer"] == 9007199254740993
    error_data(
        await definitions.client.get(ROOT + "/source", params=target), 404, "definition_not_found"
    )
    saved = await definitions.client.post(
        ROOT, content=draft.text, headers={"content-type": "application/json"}
    )
    assert saved.status_code == 201
    assert definitions.service.definition(**target) == draft.text


@pytest.mark.parametrize("revision", ["x" * 129, "line\nbreak", " emoji 😀 / +? "])
async def test_save_detail_and_source_preserve_schema_valid_identities(
    definitions: DefinitionHttp, revision: str
) -> None:
    value = json_object(decode_json(variant(revision)))
    value["graph_id"] = "a" * 160
    source = encode_json(value)
    identity = {"graph_id": "a" * 160, "revision": revision}
    response = await definitions.client.post(
        ROOT, content=source, headers={"content-type": "application/json"}
    )
    assert response.status_code == 201
    assert response.json() == {**identity, "created": True}
    detail = await definitions.client.get(ROOT + "/detail", params=identity)
    assert detail.status_code == 200
    assert detail.json()["graph_id"] == identity["graph_id"]
    assert detail.json()["revision"] == revision
    assert (await definitions.client.get(ROOT + "/source", params=identity)).text == source
