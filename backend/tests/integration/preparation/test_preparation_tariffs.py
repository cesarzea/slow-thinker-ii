"""Admission uses the latest successful validation and never rewrites historical price evidence."""

from dataclasses import replace

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore
from slow_thinker_ii.adapters.tariffs import parse_catalog
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import JsonValue, decode_json, json_object
from support.catalog import PAYLOAD
from support.operator_commands import Clock
from support.preparation import NOW, PreparationCase


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("model", "unreviewed", "tariff_model_mismatch"),
        ("review_expires_at", NOW + 90, "pricing_review_expired"),
        ("maximum_tariff_age_seconds", 1, "pricing_review_expired"),
        ("default_output_tokens", 9, "invalid_graph_or_resource_configuration"),
        ("maximum_output_tokens", 128_001, "invalid_graph_or_resource_configuration"),
        ("api_key", "must-not-be-here", "invalid_graph_or_resource_configuration"),
    ],
)
async def test_invalid_profile_blocks_start(
    case: PreparationCase, field: str, value: JsonValue, reason: str
) -> None:
    case.set_provider(field, value)
    case.clock.value += 1
    case.update()
    with pytest.raises(PreparationRejected, match=reason):
        await case.preparer().prepare(case.intent, "runtime")
    assert not case.secrets.requested


async def test_revalidation_renews_freshness_without_replacing_revision(
    case: PreparationCase,
) -> None:
    original = await case.preparer().prepare(case.intent, "runtime")
    case.clock.value += 100_000
    case.set_provider("review_expires_at", int(case.clock.value) + 3600)
    case.tariffs.publish(parse_catalog(PAYLOAD, int(case.clock.value)))
    case.update()
    renewed = await case.preparer().prepare(case.intent, "runtime-next")
    old = json_object(json_object(decode_json(original.start.snapshot_json))["tariff"])
    new = json_object(json_object(decode_json(renewed.start.snapshot_json))["tariff"])
    assert old["digest"] == new["digest"]
    assert old["retrieved_at"] == new["retrieved_at"] == NOW
    assert new["validated_at"] == case.clock.value
    assert old["validated_at"] == NOW


async def test_failed_refresh_keeps_fresh_validated_tariff(case: PreparationCase) -> None:
    case.tariffs.failed(NOW + 1, "offline")
    case.clock.value += 1
    result = await case.preparer().prepare(case.intent, "runtime")
    tariff = json_object(json_object(decode_json(result.start.snapshot_json))["tariff"])
    assert tariff["validated_at"] == NOW


async def test_regressed_clock_rejects_future_validation(case: PreparationCase) -> None:
    case.clock.value -= 1
    with pytest.raises(PreparationRejected, match="tariff_clock_regressed"):
        await case.preparer().prepare(case.intent, "runtime")


async def test_missing_tariff_prevents_credential_resolution(case: PreparationCase) -> None:
    with case.database.transaction() as connection:
        connection.execute("DELETE FROM tariff_refresh")
    with pytest.raises(PreparationRejected, match="tariff_unavailable"):
        await case.preparer().prepare(case.intent, "runtime")
    assert not case.secrets.requested


async def test_expiry_is_rechecked_inside_admission_transaction(case: PreparationCase) -> None:
    assert case.configuration is not None
    commands = SqliteOperatorStore(case.database, 1_048_576, Clock(100), case.clock)
    commands.configure(case.configuration)
    session = commands.create_session("session", "Test").receipt.target_id
    assert session is not None
    intent = replace(case.intent, session_id=session)
    workflow = await case.preparer().prepare(intent, "runtime")
    assert workflow.start.admit_before is not None
    case.clock.value = workflow.start.admit_before
    rejected = commands.admit("start", workflow.start)
    assert rejected.receipt.reason == "preparation_expired"
    assert rejected.receipt.disposition == "rejected"
    case.clock.value += 1
    assert commands.admit("start", workflow.start).replayed
