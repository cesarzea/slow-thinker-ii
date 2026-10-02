"""Malformed raw JSON and transport options fail before definition mutation."""

import pytest
from support.definition_http import ROOT, DefinitionHttp, error_data, variant


@pytest.mark.parametrize("path", [ROOT, ROOT + "/validate", ROOT + "/draft"])
@pytest.mark.parametrize(
    "body",
    [
        b"{",
        b'"\xff"',
        b'{"a":1,"a":2}',
        b'{"a":{"b":1,"b":2}}',
        b"NaN",
        b"Infinity",
        b"-Infinity",
        b"1e400",
        b"[" * 1100 + b"]" * 1100,
    ],
)
async def test_strict_json(definitions: DefinitionHttp, path: str, body: bytes) -> None:
    response = await definitions.client.post(
        path, content=body, headers={"content-type": "application/json"}
    )
    error_data(response, 400, "invalid_json")
    assert all(item.origin == "bundled" for item in definitions.service.page(100).items)


@pytest.mark.parametrize("path", [ROOT, ROOT + "/validate", ROOT + "/draft"])
@pytest.mark.parametrize("body", ["[]", "null", "{}", '"a secret value"'])
async def test_non_definition_json(definitions: DefinitionHttp, path: str, body: str) -> None:
    response = await definitions.client.post(
        path, content=body, headers={"content-type": "application/json"}
    )
    error_data(response, 422, "invalid_definition")
    assert "a secret value" not in response.text


@pytest.mark.parametrize("path", [ROOT, ROOT + "/validate", ROOT + "/draft"])
async def test_post_transport_options(definitions: DefinitionHttp, path: str) -> None:
    headers = {"content-type": "application/json"}
    error_data(
        await definitions.client.post(path + "?override=true", content=variant(), headers=headers),
        400,
        "invalid_query",
    )
    error_data(
        await definitions.client.post(
            path, content=variant(), headers={**headers, "content-encoding": "identity"}
        ),
        400,
        "unsupported_transport_options",
    )
    error_data(await definitions.client.post(path, content=variant()), 415, "json_content_required")
    error_data(
        await definitions.client.post(
            path, content=variant(), headers={"content-type": "text/plain"}
        ),
        415,
        "json_content_required",
    )
    error_data(
        await definitions.client.post(
            path, content=variant(), headers=[("content-type", "application/json")] * 2
        ),
        415,
        "json_content_required",
    )


@pytest.mark.parametrize("suffix", ["/detail", "/source"])
@pytest.mark.parametrize(
    "query",
    [
        "",
        "?graph_id=single-agent",
        "?graph_id=X&revision=x",
        "?graph_id=single-agent&revision=",
        "?graph_id=single-agent&revision=x&revision=y",
        "?graph_id=single-agent&revision=x&other=y",
    ],
)
async def test_exact_get_queries(definitions: DefinitionHttp, suffix: str, query: str) -> None:
    error_data(await definitions.client.get(ROOT + suffix + query), 400, "invalid_query")
