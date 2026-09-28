"""Unapproved, stale and invalid inputs cannot reach component execution."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import BundledDefinitionStore
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object
from support.preparation import PreparationCase


@pytest.mark.parametrize("configuration", [None, "other-revision"])
async def test_configuration_must_match_selection(
    case: PreparationCase, configuration: str | None
) -> None:
    assert case.configuration is not None
    case.configuration = (
        None if configuration is None else replace(case.configuration, revision=configuration)
    )
    with pytest.raises(PreparationRejected, match="configuration_unavailable"):
        await case.preparer().prepare(case.intent, "runtime")


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True])
async def test_invalid_clock(case: PreparationCase, value: float) -> None:
    case.clock.value = value
    with pytest.raises(PreparationRejected, match="invalid_preparation_clock"):
        await case.preparer().prepare(case.intent, "runtime")


async def test_limits_profile_must_match_graph(case: PreparationCase) -> None:
    assert case.configuration is not None
    case.configuration = replace(
        case.configuration, limits=replace(case.configuration.limits, revision="other")
    )
    with pytest.raises(PreparationRejected, match="limits_profile_mismatch"):
        await case.preparer().prepare(case.intent, "runtime")


@pytest.mark.parametrize(
    "field,value",
    [
        ("graph_id", "../../outside"),
        ("graph_revision", "missing"),
        ("input_json", '{"unrecognised":true}'),
    ],
)
async def test_graph_and_input_are_validated(case: PreparationCase, field: str, value: str) -> None:
    with pytest.raises(PreparationRejected, match="invalid_graph_or_resource_configuration"):
        await case.preparer().prepare(replace(case.intent, **{field: value}), "runtime")


@pytest.mark.parametrize("value", ['{"schema_version":"2"}', '{"api_key":"forbidden"}'])
async def test_configuration_schema_is_strict(case: PreparationCase, value: str) -> None:
    assert case.configuration is not None
    case.configuration = replace(case.configuration, resources_json=value)
    with pytest.raises(PreparationRejected, match="invalid_graph_or_resource_configuration"):
        await case.preparer().prepare(case.intent, "runtime")


def choices(case: PreparationCase) -> list[JsonValue]:
    value = case.settings["installations"]
    assert isinstance(value, list)
    return value


@pytest.mark.parametrize(
    "change,reason",
    [
        ("duplicate", "installation_selection_invalid"),
        ("unknown", "installation_selection_invalid"),
        ("missing", "host_adapter_unavailable"),
        ("adapter", "host_adapter_unavailable"),
        ("resolution", "component_preparation_unavailable"),
    ],
)
async def test_only_explicit_installed_types_and_adapters(
    case: PreparationCase, change: str, reason: str
) -> None:
    selected = choices(case)
    item = json_object(selected[0])
    if change == "duplicate":
        selected.append(item)
    elif change == "missing":
        selected.pop(0)
    else:
        field = {"unknown": "type_id", "adapter": "host_adapter", "resolution": "resolution_id"}[
            change
        ]
        item[field] = "f" * 32 if change == "resolution" else "not-registered"
        selected[0] = item
    case.update()
    with pytest.raises(PreparationRejected, match=reason):
        await case.preparer().prepare(case.intent, "runtime")


async def test_duplicate_trusted_descriptor(case: PreparationCase) -> None:
    case.descriptors += case.descriptors[:1]
    with pytest.raises(PreparationRejected, match="invalid_graph_or_resource_configuration"):
        await case.preparer().prepare(case.intent, "runtime")


@pytest.mark.parametrize("profile", [{}, {"missing": {}}])
async def test_missing_provider(case: PreparationCase, profile: JsonObject) -> None:
    case.settings["providers"] = profile
    case.update()
    reason = (
        "provider_profile_unavailable" if not profile else "invalid_graph_or_resource_configuration"
    )
    with pytest.raises(PreparationRejected, match=reason):
        await case.preparer().prepare(case.intent, "runtime")


async def test_missing_definition_files(case: PreparationCase, tmp_path: Path) -> None:
    case.definitions = BundledDefinitionStore(tmp_path / "missing")
    with pytest.raises(PreparationRejected, match="component_preparation_unavailable"):
        await case.preparer().prepare(case.intent, "runtime")
