"""Model price histories preserve independent latest validity and frozen old evidence."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import (
    SqliteModelTariffReader,
    SqliteModelTariffStore,
    SqliteTariffStore,
)
from slow_thinker_ii.adapters.tariffs import parse_catalog, parse_deepseek_pricing
from support.catalog import PAYLOAD
from support.operator_commands import operator_case
from support.workspace_tariffs import DEEPSEEK_PAYLOAD

PROFILE = "deepseek.flash.direct.v1"
OPENAI = "openai.gpt-6-luna.standard.text.v1"


def test_scoped_latest_price_failure_and_old_revision_retention(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    reader = SqliteModelTariffReader(case.database)
    store = SqliteModelTariffStore(case.database, PROFILE)
    assert reader.selected(PROFILE) is None and reader.selected(OPENAI) is None
    now = int(case.wall())
    original = parse_deepseek_pricing(DEEPSEEK_PAYLOAD, now)
    store.publish(original)
    store.publish(replace(original, retrieved_at=now + 10))
    store.failed(now + 20, "invalid_source")
    selected = reader.selected(PROFILE)
    assert selected is not None and selected.validated_at == now + 10
    assert selected.revision == original
    assert store.status().error == "invalid_source"
    assert store.status().last_attempt == now + 20
    assert reader.selected(OPENAI) is None
    assert store.revision(original.digest) == original
    changed = parse_deepseek_pricing(
        DEEPSEEK_PAYLOAD.replace(b"$0.3", b"$0.32").replace(b"$0.15", b"$0.16"), now + 30
    )
    store.publish(changed)
    assert store.revision(original.digest) == original
    latest = reader.selected(PROFILE)
    assert latest is not None and latest.revision.digest == changed.digest
    legacy = parse_catalog(PAYLOAD, now)
    SqliteTariffStore(case.database).publish(legacy)
    selected_openai, selected_deepseek = reader.selected(OPENAI), reader.selected(PROFILE)
    assert selected_openai is not None and selected_openai.revision == legacy
    assert selected_deepseek is not None and selected_deepseek.revision == changed


def test_failed_first_refresh_unknown_revision_and_profile_identity(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    store = SqliteModelTariffStore(case.database, PROFILE)
    store.failed(100, "unavailable")
    status = store.status()
    assert status.last_success is None and status.revision is None
    assert SqliteModelTariffReader(case.database).selected(PROFILE) is None
    with pytest.raises(ValueError, match="Unknown"):
        store.revision("not-a-revision")
    with pytest.raises(ValueError, match="does not match"):
        store.publish(parse_catalog(PAYLOAD, int(case.wall())))
    for identity in ("", OPENAI):
        with pytest.raises(ValueError, match="legacy"):
            SqliteModelTariffStore(case.database, identity)
