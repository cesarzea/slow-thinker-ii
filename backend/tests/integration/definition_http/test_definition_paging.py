"""Signed HTTP pages preserve their first insertion window and size binding."""

import pytest
from slow_thinker_ii.contracts import json_object
from support.definition_http import ROOT, DefinitionHttp, error_data, variant


async def test_pages_exclude_new_saves_until_explicit_refresh(definitions: DefinitionHttp) -> None:
    for revision in ("first", "second", "third"):
        definitions.service.save(variant(revision))
    response = await definitions.client.get(ROOT, params={"limit": 2})
    page = json_object(response.json())
    definitions.service.save(variant("late"))
    all_items: list[object] = []
    while True:
        items = page["items"]
        assert isinstance(items, list) and len(items) <= 2
        all_items.extend(items)
        cursor = page["next_cursor"]
        if cursor is None:
            break
        assert isinstance(cursor, str)
        page = json_object(
            (await definitions.client.get(ROOT, params={"limit": 2, "cursor": cursor})).json()
        )
        assert len(all_items) <= 100
    personal = [
        json_object(item) for item in all_items if json_object(item)["origin"] == "personal"
    ]
    assert [item["revision"] for item in personal] == ["first", "second", "third"]
    origins = [str(json_object(item)["origin"]) for item in all_items]
    assert origins == sorted(origins)
    fresh = (await definitions.client.get(ROOT, params={"limit": 100})).json()
    assert fresh["items"][-1]["revision"] == "late"


async def test_signed_cursor_rejects_tampering_and_page_size_change(
    definitions: DefinitionHttp,
) -> None:
    first = (await definitions.client.get(ROOT, params={"limit": 1})).json()
    cursor = first["next_cursor"]
    assert isinstance(cursor, str)
    error_data(
        await definitions.client.get(ROOT, params={"limit": 2, "cursor": cursor}),
        400,
        "invalid_cursor",
    )
    error_data(
        await definitions.client.get(ROOT, params={"limit": 1, "cursor": cursor + "x"}),
        400,
        "invalid_cursor",
    )


@pytest.mark.parametrize(
    "query,code",
    [
        ("?limit=0", "invalid_query"),
        ("?limit=101", "invalid_query"),
        ("?limit=-1", "invalid_query"),
        ("?limit=x", "invalid_query"),
        ("?limit=1&limit=1", "invalid_query"),
        ("?extra=true", "invalid_query"),
        ("?cursor=", "invalid_cursor"),
        ("?cursor=bad", "invalid_cursor"),
        ("?cursor=a&cursor=b", "invalid_query"),
    ],
)
async def test_page_query_bindings(definitions: DefinitionHttp, query: str, code: str) -> None:
    error_data(await definitions.client.get(ROOT + query), 400, code)
