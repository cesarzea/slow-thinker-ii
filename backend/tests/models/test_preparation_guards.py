"""Misbound profiles, malformed source capture and unsafe workspace fail before launch."""

from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.preparation import (
    ModelResourceAdapter,
    OpenAIClientAdapter,
    OpenAIResourceAdapter,
    ResourceSettings,
    ServiceEndpoints,
)
from slow_thinker_ii.adapters.sqlite import SqliteModelTariffReader
from slow_thinker_ii.application import PreparationRejected, workspace
from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from models.preparation_fixture import ModelInstallations, model_preparer, preparation_case
from models.preparation_guards import FrozenReader, RecordingModelAdapter
from models.test_preparation import installed_models

__all__ = ["installed_models"]


async def test_public_adapters_reject_missing_or_mismatched_bindings(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    adapter = RecordingModelAdapter()
    case.adapters["model-resource"] = adapter
    await model_preparer(case, definitions, SqliteModelTariffReader(case.database)).prepare(
        case.intent, "runtime"
    )
    request = adapter.requests[0]
    assert request.tariff is not None
    selected = replace(
        request.tariff,
        revision=replace(
            request.tariff.revision,
            tariff=replace(request.tariff.revision.tariff, profile="wrong-billing-id"),
        ),
    )
    with pytest.raises(PreparationRejected, match="tariff_billing_profile_mismatch"):
        ModelResourceAdapter().configure(replace(request, tariff=selected))
    case.settings["providers"] = {}
    empty = ResourceSettings.model_validate_json(encode_json(case.settings))
    with pytest.raises(PreparationRejected, match="provider_profile_unavailable"):
        ModelResourceAdapter().configure(replace(request, settings=empty))
    with pytest.raises(PreparationRejected, match="legacy_provider_profile_mismatch"):
        OpenAIResourceAdapter().configure(request)
    with pytest.raises(PreparationRejected, match="model_resource_required"):
        OpenAIClientAdapter().configure(
            replace(request, component=request.component.model_copy(update={"resources": {}}))
        )


async def test_malformed_digest_bound_capture_cannot_enter_saved_snapshot(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    selection = SqliteModelTariffReader(case.database).selected("deepseek.flash.direct.v1")
    assert selection is not None
    source = json_object(decode_json(selection.revision.source_json))
    source["captured_html"] = 1
    encoded = encode_json(source)
    revision = replace(
        selection.revision, source_json=encoded, digest=sha256(encoded.encode()).hexdigest()
    )
    reader = FrozenReader(workspace.ModelTariffSelection(revision, selection.validated_at))
    with pytest.raises(PreparationRejected, match="invalid_tariff_source_capture"):
        await model_preparer(case, definitions, reader).prepare(case.intent, "runtime")
    assert not (case.directory / "runtime").exists()


async def test_workspace_path_and_deepseek_endpoint_are_trusted(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    case.directory = Path("relative-workspace")
    with pytest.raises(ValueError, match="absolute workspace"):
        model_preparer(case, definitions, None)
    valid = ServiceEndpoints("http://127.0.0.1:123/v1", deepseek_provider="http://127.0.0.1:456/v1")
    assert valid.deepseek_provider.endswith("456/v1")
    with pytest.raises(ValueError):
        ServiceEndpoints("http://127.0.0.1:123/v1", deepseek_provider="https://other.example")
