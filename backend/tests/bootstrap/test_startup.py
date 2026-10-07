"""Startup failures name what to fix: secrets, the interface, installations, the factory."""

from collections.abc import Mapping
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slow_thinker_ii.bootstrap import AppOverrides, configured_app, create_app, load_configuration
from slow_thinker_ii.contracts import JsonObject
from support.clock import FakeClock
from support.examples import changed
from support.providers import ScriptedProvider

from .configurations import ENVIRONMENT, SECRETS, TOKEN, local, written


def app_from(
    directory: Path,
    environment: Mapping[str, str],
    overrides: AppOverrides | None = None,
    document: JsonObject | None = None,
) -> FastAPI:
    source = local(directory) if document is None else document
    configuration = load_configuration(written(directory, source))
    return create_app(configuration, environment, overrides)


@pytest.mark.parametrize("token", [None, "", "too-short", "x" * 129, "with spaces " * 4])
def test_the_operator_token_is_required_and_never_shown(tmp_path: Path, token: str | None) -> None:
    environment = dict(SECRETS)
    if token is not None:
        environment["SLOW_THINKER_OPERATOR_TOKEN"] = token
    with pytest.raises(ValueError, match="SLOW_THINKER_OPERATOR_TOKEN") as raised:
        app_from(tmp_path, environment)
    assert not token or token not in str(raised.value)


def test_provider_keys_come_from_the_environment_unless_the_provider_is_replaced(
    tmp_path: Path,
) -> None:
    without_keys = {"SLOW_THINKER_OPERATOR_TOKEN": TOKEN}
    with pytest.raises(ValueError, match="OPENAI_API_KEY .*is not set"):
        app_from(tmp_path, without_keys)
    assert isinstance(app_from(tmp_path, ENVIRONMENT), FastAPI)
    replaced = AppOverrides(provider=ScriptedProvider(FakeClock()))
    assert isinstance(app_from(tmp_path, without_keys, replaced), FastAPI)


def test_a_configured_interface_must_exist_and_is_served(tmp_path: Path) -> None:
    missing = changed(local(tmp_path), ("server", "static_directory"), str(tmp_path / "dist"))
    with pytest.raises(ValueError) as raised:
        app_from(tmp_path, ENVIRONMENT, document=missing)
    assert str(raised.value) == (
        f"The interface directory {tmp_path / 'dist'} does not exist. Build it with "
        '"npm run build", or set server.static_directory to null.'
    )
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist/index.html").write_text("<title>Slow Thinker II</title>")
    app = app_from(tmp_path, ENVIRONMENT, document=missing)
    with TestClient(app, base_url="http://127.0.0.1:8000") as client:
        assert "Slow Thinker II" in client.get("/").text


def test_hosts_and_origins_the_operator_guard_refuses_are_located(tmp_path: Path) -> None:
    document = changed(local(tmp_path), ("server", "allowed_origins"), ["localhost:5173"])
    with pytest.raises(ValueError) as raised:
        app_from(tmp_path, ENVIRONMENT, document=document)
    assert str(raised.value) == (
        "Invalid server configuration: /server: The allowed origin “localhost:5173” must be "
        "exactly scheme://host[:port]."
    )


def test_configured_installations_are_verified_unless_both_are_replaced(tmp_path: Path) -> None:
    placeholders = changed(local(tmp_path), ("components", "resolutions"), ["from-make"])
    with pytest.raises(ValueError, match="Invalid installation identity"):
        app_from(tmp_path, ENVIRONMENT, document=placeholders)
    only_declarations = AppOverrides(components=())
    with pytest.raises(ValueError, match="Invalid installation identity"):
        app_from(tmp_path, ENVIRONMENT, only_declarations, placeholders)
    both = AppOverrides(components=(), launch_targets=ScriptedTargets())
    assert isinstance(app_from(tmp_path, ENVIRONMENT, both, placeholders), FastAPI)


def test_the_factory_reads_the_named_configuration_or_exits_with_the_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name, value in ENVIRONMENT.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("SLOW_THINKER_CONFIGURATION", raising=False)
    with pytest.raises(SystemExit, match="SLOW_THINKER_CONFIGURATION must name the file"):
        configured_app()
    monkeypatch.setenv("SLOW_THINKER_CONFIGURATION", str(tmp_path / "missing.json"))
    with pytest.raises(SystemExit, match="cannot start: Cannot read the server configuration"):
        configured_app()
    monkeypatch.setenv("SLOW_THINKER_CONFIGURATION", str(written(tmp_path, local(tmp_path))))
    assert isinstance(configured_app(), FastAPI)
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    with pytest.raises(SystemExit, match="DEEPSEEK_API_KEY"):
        configured_app()


class ScriptedTargets:
    """Launch targets that are never used: no run starts in these tests."""

    def interpreter(self, ref: object) -> Path:
        raise AssertionError(ref)

    def module(self, ref: object) -> str:
        raise AssertionError(ref)
