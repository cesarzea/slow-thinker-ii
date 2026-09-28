"""Startup configuration is explicit, strict, credential-free and resolved relative to its file."""

from pathlib import Path

import pytest
from slow_thinker_ii.bootstrap import configured_app, load_execution_setup
from slow_thinker_ii.contracts import JsonValue, encode_json, json_object
from support.operator_http import TOKEN
from support.startup_configuration import startup_record


@pytest.fixture
def configured_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "execution.json"
    path.write_text(encode_json(startup_record(tmp_path)))
    monkeypatch.setenv("SLOW_THINKER_TEST_OPERATOR_TOKEN", TOKEN)
    monkeypatch.delenv("SLOW_THINKER_TEST_PROVIDER_KEY", raising=False)
    return path


def test_configuration_loads_without_resolving_provider_key(configured_file: Path) -> None:
    setup = load_execution_setup(configured_file)
    assert setup.workspace == configured_file.parent / "runs"
    assert setup.configuration.revision == "startup-1"
    assert len(setup.descriptors) == 3
    assert TOKEN not in repr(setup) and TOKEN not in setup.configuration.to_json()
    assert setup.configuration.limits.month_budget == 10000


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", "2"),
        ("maximum_commands", 0),
        ("preparation_seconds", True),
        ("gateway_url", "https://remote.example/v1"),
        ("operator_credential_env", "bad-name"),
        ("api_key", "unwanted-secret"),
    ],
)
def test_invalid_configuration_fields(configured_file: Path, field: str, value: JsonValue) -> None:
    import json

    record = json_object(json.loads(configured_file.read_text()))
    record[field] = value
    configured_file.write_text(encode_json(record))
    with pytest.raises(ValueError, match="Invalid or unavailable") as caught:
        load_execution_setup(configured_file)
    assert "unwanted-secret" not in str(caught.value)


def test_missing_operator_credential_is_explicit(
    configured_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SLOW_THINKER_TEST_OPERATOR_TOKEN")
    with pytest.raises(ValueError, match="Invalid or unavailable"):
        load_execution_setup(configured_file)


@pytest.mark.parametrize(
    "text", ['{"schema_version":"1","schema_version":"2"}', "[]", "x" * 1_048_577]
)
def test_invalid_startup_document_is_bounded(configured_file: Path, text: str) -> None:
    configured_file.write_text(text)
    with pytest.raises(ValueError, match="Invalid or unavailable"):
        load_execution_setup(configured_file)


def test_legacy_key_file_is_not_opened(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        del args, kwargs
        pytest.fail("A key file must not be opened")

    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(ValueError, match="Invalid or unavailable"):
        load_execution_setup(tmp_path / "slow-thinker.keys.json")


def test_factory_enables_commands_only_with_explicit_configuration(
    configured_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SLOW_THINKER_CONFIGURATION", raising=False)
    assert "/api/v1/runs" not in configured_app().openapi()["paths"]
    monkeypatch.setenv("SLOW_THINKER_CONFIGURATION", str(configured_file))
    assert "/api/v1/runs" in configured_app().openapi()["paths"]


def test_invalid_factory_configuration_does_not_fall_back_to_viewer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SLOW_THINKER_CONFIGURATION", str(tmp_path / "missing.json"))
    with pytest.raises(ValueError, match="Invalid or unavailable"):
        configured_app()
