"""Daily cadence, atomic snapshots and failure recovery with the real SQLite adapter."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteTariffStore
from slow_thinker_ii.application import REFRESH_SECONDS, TariffRefresh
from support.catalog import PAYLOAD, RecordedCatalog


def store_at(path: Path) -> SqliteTariffStore:
    database = SqliteDatabase(path)
    database.initialize()
    return SqliteTariffStore(database)


async def test_daily_schedule_and_restart_preserve_old_revisions(tmp_path: Path) -> None:
    source = RecordedCatalog()
    store = store_at(tmp_path / "prices.sqlite")
    refresh = TariffRefresh(source, store)
    first = await refresh.refresh_due(1)
    assert first.revision is not None
    original = store.revision(first.revision)
    source.payload = PAYLOAD.replace(b'"0.0000001"', b'"0.00000015"')
    await refresh.refresh_due(REFRESH_SECONDS)
    assert source.calls == 1
    latest = await refresh.refresh_due(REFRESH_SECONDS + 1)
    assert source.calls == 2
    assert latest.revision != first.revision
    reopened = store_at(tmp_path / "prices.sqlite")
    assert reopened.status() == latest
    assert reopened.revision(first.revision) == original
    await TariffRefresh(source, reopened).refresh_due(REFRESH_SECONDS + 2, startup=True)
    assert source.calls == 2


@pytest.mark.parametrize("error", [OSError("offline"), ValueError("new billing semantics")])
async def test_failed_refresh_preserves_validated_prices(tmp_path: Path, error: Exception) -> None:
    source = RecordedCatalog()
    store = store_at(tmp_path / "prices.sqlite")
    refresh = TariffRefresh(source, store)
    original = await refresh.refresh_due(0)
    assert isinstance(error, OSError | ValueError)
    source.error = error
    failed = await refresh.refresh_due(REFRESH_SECONDS)
    assert failed.revision == original.revision
    assert failed.last_success == 0
    assert failed.error == type(error).__name__
    source.error = None
    recovered = await refresh.refresh_due(REFRESH_SECONDS + 1, startup=True)
    assert recovered.error is None
    assert recovered.last_success == REFRESH_SECONDS + 1


async def test_missing_prices_retry_on_startup_and_calls_serialize(tmp_path: Path) -> None:
    source = RecordedCatalog()
    source.error = OSError("offline")
    refresh = TariffRefresh(source, store_at(tmp_path / "prices.sqlite"))
    missing = await refresh.refresh_due(0)
    assert missing.revision is None
    source.error = None
    await asyncio.gather(*(refresh.refresh_due(1, startup=True) for _ in range(10)))
    assert source.calls == 2
    await refresh.refresh_due(0)
    assert source.calls == 2


def test_unknown_revision_is_not_substituted(tmp_path: Path) -> None:
    store = store_at(tmp_path / "prices.sqlite")
    with pytest.raises(ValueError, match="Unknown tariff"):
        store.revision("unavailable")
