"""Published revisions cannot change admitted policy evidence or exact quanta rounding."""

from dataclasses import replace
from pathlib import Path

from slow_thinker_ii.adapters.models import ModelPricePolicy
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteModelTariffReader,
    SqliteModelTariffStore,
)
from slow_thinker_ii.adapters.tariffs import DEEPSEEK_PROFILE_ID, parse_deepseek_pricing
from support.preparation import NOW
from support.workspace_tariffs import DEEPSEEK_PAYLOAD

from models.fixtures import arguments, payload, policy, profile, result


def test_refresh_leaves_old_quote_result_and_policy_unchanged(tmp_path: Path) -> None:
    database = SqliteDatabase(tmp_path / "price-history.sqlite")
    database.initialize()
    store = SqliteModelTariffStore(database, DEEPSEEK_PROFILE_ID)
    original = profile()
    store.publish(original.revision)
    admitted = ModelPricePolicy(original)
    quote, settled = admitted.quote(arguments()), admitted.reconcile(result(payload()))
    changed = DEEPSEEK_PAYLOAD.replace(b"$0.003", b"$0.004").replace(b"$0.006", b"$0.008")
    store.publish(parse_deepseek_pricing(changed, NOW + 86400))
    latest = SqliteModelTariffReader(database).selected(DEEPSEEK_PROFILE_ID)
    assert latest is not None and latest.revision != original.revision
    assert admitted.quote(arguments()) == quote and admitted.reconcile(result(payload())) == settled
    assert settled.amount == 6024 and store.revision(original.revision.digest) == original.revision
    fresh = ModelPricePolicy(replace(original, revision=latest.revision))
    assert fresh.reconcile(result(payload())).amount == 6032


def test_fractional_native_rates_round_up_once_after_category_sum() -> None:
    changed = DEEPSEEK_PAYLOAD.replace(b"$0.003", b"$0.00000003").replace(b"$0.006", b"$0.00000006")
    selected = replace(profile(), revision=parse_deepseek_pricing(changed, NOW))
    evidence = ModelPricePolicy(selected).reconcile(result(payload()))
    assert evidence.amount == 6001
    assert policy().quote(arguments()).bound == 300_009_600
