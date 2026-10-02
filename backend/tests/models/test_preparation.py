"""Production admission freezes scoped tariffs and retains old positional preparation callers."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.preparation import (
    ResourceSettings,
    model_capabilities,
    standard_host_adapters,
)
from slow_thinker_ii.adapters.sqlite import SqliteModelTariffReader, SqliteModelTariffStore
from slow_thinker_ii.adapters.tariffs import DEEPSEEK_PROFILE_ID, parse_deepseek_pricing
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.preparation import NOW, PreparationCase
from support.workspace_tariffs import DEEPSEEK_PAYLOAD

from models.preparation_fixture import (
    ModelInstallations,
    model_installations,
    model_preparer,
    preparation_case,
)


@pytest.fixture(scope="module")
def installed_models(tmp_path_factory: pytest.TempPathFactory) -> ModelInstallations:
    return model_installations(tmp_path_factory.mktemp("model-installations"))


async def test_saved_scoped_tariff_freezes_exact_resource_snapshot(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    reader = SqliteModelTariffReader(case.database)
    assert reader.selected("deepseek-flash") is None
    workflow = await model_preparer(case, definitions, reader).prepare(
        case.intent, "models-runtime"
    )
    frozen = workflow.start.snapshot_json
    snapshot = json_object(decode_json(frozen))
    model = json_object(json_object(snapshot["instances"])["model"])
    selected = reader.selected(DEEPSEEK_PROFILE_ID)
    assert selected is not None
    assert json_object(model["model_tariff"])["digest"] == selected.revision.digest
    assert json_object(model["config"])["provider"] == "deepseek"
    assert json_object(model["config"])["model_alias"] == "deepseek-alias"
    assert json_object(json_object(model["model_tariff"])["billing"])["schedule"]
    assert json_object(snapshot["tariff"])["digest"] != selected.revision.digest
    assert "synthetic-preparation-key" not in frozen and "captured_html" not in frozen
    changed = DEEPSEEK_PAYLOAD.replace(b"$0.003", b"$0.004").replace(b"$0.006", b"$0.008")
    SqliteModelTariffStore(case.database, DEEPSEEK_PROFILE_ID).publish(
        parse_deepseek_pricing(changed, NOW + 1)
    )
    assert workflow.start.snapshot_json == frozen
    assert reader.selected(DEEPSEEK_PROFILE_ID) != selected
    assert workflow.environment.report() == "[]"


async def test_old_openai_preparer_and_new_openai_without_scoped_reader_remain_valid(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    legacy = PreparationCase(tmp_path, installed_models.directory, installed_models.selected)
    original = await legacy.preparer().prepare(legacy.intent, "legacy-runtime")
    assert original.models and '"provider":"deepseek"' not in original.start.snapshot_json
    case, definitions = await preparation_case(tmp_path / "new", installed_models)
    source = json_object(decode_json(definitions.source))
    model = json_object(json_object(source["components"])["model"])
    model["config"] = {"provider_profile": "openai-luna", "model": "openai-alias"}
    source["components"] = {**json_object(source["components"]), "model": model}
    definitions.source = encode_json(source)
    prepared = await model_preparer(case, definitions, None).prepare(case.intent, "openai-runtime")
    model = json_object(
        json_object(json_object(decode_json(prepared.start.snapshot_json))["instances"])["model"]
    )
    assert json_object(model["config"])["provider"] == "openai"
    assert (
        json_object(model["model_tariff"])["digest"]
        == json_object(json_object(decode_json(prepared.start.snapshot_json))["tariff"])["digest"]
    )


@pytest.mark.parametrize(
    "fault,reason",
    [
        ("reader", "tariff_unavailable"),
        ("profile", "provider_profile_unavailable"),
        ("billing", "tariff_unavailable"),
        ("expired", "pricing_review_expired"),
    ],
)
async def test_unavailable_or_stale_resources_fail_before_host_launch(
    tmp_path: Path, installed_models: ModelInstallations, fault: str, reason: str
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    providers = json_object(case.settings["providers"])
    profile = json_object(providers["deepseek-flash"])
    if fault == "profile":
        providers.pop("deepseek-flash")
    elif fault == "billing":
        profile["billing_profile"] = "unavailable-profile"
    elif fault == "expired":
        profile["review_expires_at"] = NOW
    if fault != "profile":
        providers["deepseek-flash"] = profile
    case.settings["providers"] = providers
    case.update()
    reader = None if fault == "reader" else SqliteModelTariffReader(case.database)
    with pytest.raises(PreparationRejected, match=reason):
        await model_preparer(case, definitions, reader).prepare(case.intent, "runtime")
    assert not (case.directory / "runtime").exists() and not case.secrets.requested


def test_discovery_exposes_reviewed_capabilities_and_registered_adapters() -> None:
    from support.workspace_data import workspace_resources

    settings = ResourceSettings.model_validate_json(encode_json(workspace_resources()))
    capabilities = model_capabilities(settings)
    assert [value["provider_profile"] for value in capabilities] == sorted(settings.providers)
    deepseek = next(value for value in capabilities if value["provider"] == "deepseek")
    assert deepseek["reasoning_efforts"] == ["none", "low", "high", "max"]
    assert deepseek["supports_temperature"] is True and "credential_ref" not in str(capabilities)
    assert {"model-resource", "openai-resource", "plain", "openai-client"} <= set(
        standard_host_adapters()
    )
