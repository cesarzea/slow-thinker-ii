"""A bounded source refresh cannot replace another profile or previous valid prices."""

from pathlib import Path

import httpx
import pytest
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteModelTariffReader,
    SqliteModelTariffStore,
    SqliteTariffStore,
)
from slow_thinker_ii.adapters.tariffs import DEEPSEEK_PROFILE_ID, DeepSeekTariffSource
from slow_thinker_ii.application import REFRESH_SECONDS, TariffRefresh
from support.catalog import RecordedCatalog
from support.workspace_tariffs import DEEPSEEK_PAYLOAD, RecordedDeepSeek


@pytest.mark.parametrize("fault", ["none", "http", "timeout", "mime", "size", "semantics"])
async def test_source_download_is_bounded_and_validates_content(fault: str) -> None:
    calls: list[httpx.Request] = []

    source = download_fixture(fault, calls)
    if fault == "none":
        assert (await source.fetch(1)).tariff.profile == DEEPSEEK_PROFILE_ID
    else:
        with pytest.raises(OSError if fault in {"http", "timeout"} else ValueError):
            await source.fetch(1)
    assert len(calls) == 1


def download_fixture(fault: str, calls: list[httpx.Request]) -> DeepSeekTariffSource:
    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.url.scheme == "https" and request.headers["accept-encoding"] == "identity"
        if fault == "timeout":
            raise httpx.ReadTimeout("recorded outage", request=request)
        body = (
            b"x" * (256 * 1024 + 1)
            if fault == "size"
            else b"malformed"
            if fault == "semantics"
            else DEEPSEEK_PAYLOAD
        )
        return httpx.Response(
            500 if fault == "http" else 200,
            content=body,
            headers={
                "content-type": "application/json"
                if fault == "mime"
                else "text/html; charset=utf-8"
            },
        )

    return DeepSeekTariffSource(httpx.MockTransport(handle))


async def test_daily_sources_are_independent_and_preserve_valid_history(tmp_path: Path) -> None:
    database = SqliteDatabase(tmp_path / "tariffs.sqlite")
    database.initialize()
    openai_store, direct_store = (
        SqliteTariffStore(database),
        SqliteModelTariffStore(database, DEEPSEEK_PROFILE_ID),
    )
    catalog = RecordedCatalog()
    openai_refresh = TariffRefresh(catalog, openai_store)
    direct_refresh = TariffRefresh(RecordedDeepSeek(), direct_store)
    first_openai, first_direct = (
        await openai_refresh.refresh_due(1),
        await direct_refresh.refresh_due(1),
    )
    assert first_openai.revision is not None and first_direct.revision is not None
    original = direct_store.revision(first_direct.revision)
    failure = download_fixture("semantics", [])
    failed = await TariffRefresh(failure, direct_store).refresh_due(REFRESH_SECONDS + 1)
    assert (
        failed.revision == first_direct.revision
        and failed.last_success == 1
        and failed.error == "ValueError"
    )
    assert openai_store.status() == first_openai
    await openai_refresh.refresh_due(REFRESH_SECONDS)
    assert catalog.calls == 1
    await openai_refresh.refresh_due(REFRESH_SECONDS + 1)
    assert catalog.calls == 2 and direct_store.revision(first_direct.revision) == original
    selected = SqliteModelTariffReader(database).selected(DEEPSEEK_PROFILE_ID)
    assert selected is not None and selected.revision == original
