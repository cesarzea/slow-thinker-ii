"""Complete success/error bounds and failures after insertion never leak private diagnostics."""

from pathlib import Path
from typing import Never

import pytest
from slow_thinker_ii.adapters.http import definition_router
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import json_object
from support.definition_http import (
    ROOT,
    DefinitionHttp,
    definition_http,
    error_data,
    reference,
    variant,
)


async def test_complete_representations_are_rejected_without_truncation(tmp_path: Path) -> None:
    case = definition_http(tmp_path, 64)
    try:
        case.service.save(variant())
        for path in (ROOT, ROOT + "/source", ROOT + "/detail"):
            params = {} if path == ROOT else reference()
            error_data(await case.client.get(path, params=params), 413, "response_too_large")
        error_data(
            await case.client.post(
                ROOT, content=variant(), headers={"content-type": "application/json"}
            ),
            413,
            "request_too_large",
        )
        response = await case.client.post(
            ROOT + "/draft", json={"source": reference(), "target": reference("new")}
        )
        error_data(response, 413, "request_too_large")
    finally:
        await case.client.aclose()


async def test_error_envelopes_fit_utf8_cap_even_with_tiny_payload_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = definition_http(tmp_path, 1)
    issues = tuple(
        library.DefinitionIssue("/" + "界" * 150, "Invalid " + "界" * 150) for _ in range(20)
    )

    def invalid(_: str) -> Never:
        raise library.DefinitionError("invalid_definition", issues)

    monkeypatch.setattr(case.service, "validate", invalid)
    try:
        response = await case.client.post(
            ROOT + "/validate", content="0", headers={"content-type": "application/json"}
        )
        error = error_data(response, 422, "invalid_definition")
        diagnostics = error["issues"]
        assert isinstance(diagnostics, list) and 0 < len(diagnostics) < 10
        assert len(response.content) > 1
        for issue in diagnostics:
            value = json_object(issue)
            assert len(str(value["pointer"])) <= 160 and len(str(value["message"])) <= 160
    finally:
        await case.client.aclose()


async def test_oversized_issue_fields_have_fixed_fallbacks(
    definitions: DefinitionHttp, monkeypatch: pytest.MonkeyPatch
) -> None:
    def invalid(_: str) -> Never:
        raise library.DefinitionError(
            "invalid_definition", (library.DefinitionIssue("private" * 30, "secret" * 30),)
        )

    monkeypatch.setattr(definitions.service, "validate", invalid)
    response = await definitions.client.post(ROOT + "/validate", json={})
    error = error_data(response, 422, "invalid_definition")
    assert error["issues"] == [{"pointer": "", "message": "The definition is invalid."}]
    assert "private" not in response.text and "secret" not in response.text


async def test_uncertain_save_failure_can_be_recovered_by_exact_replay(
    definitions: DefinitionHttp, monkeypatch: pytest.MonkeyPatch
) -> None:
    save = definitions.service.save

    def fail_after_insert(source: str) -> Never:
        save(source)
        raise RuntimeError("credential secret /private/internal.sqlite")

    monkeypatch.setattr(definitions.service, "save", fail_after_insert)
    response = await definitions.client.post(
        ROOT, content=variant(), headers={"content-type": "application/json"}
    )
    error_data(response, 503, "operator_service_unavailable")
    assert "credential" not in response.text and "/private/" not in response.text
    assert definitions.service.definition(**reference()) == variant()
    monkeypatch.setattr(definitions.service, "save", save)
    replay = await definitions.client.post(
        ROOT, content=variant(), headers={"content-type": "application/json"}
    )
    assert replay.status_code == 200 and replay.json()["created"] is False


@pytest.mark.parametrize("limit", [0, -1, True])
def test_router_requires_positive_integer_bound(definitions: DefinitionHttp, limit: int) -> None:
    with pytest.raises(ValueError):
        definition_router(definitions.service, limit)
