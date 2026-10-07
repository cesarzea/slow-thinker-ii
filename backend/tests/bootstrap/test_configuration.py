"""The step 1 example configuration, relative paths, defaults and model settings."""

from pathlib import Path

import pytest
from slow_thinker_ii.application import BudgetLimits, RunSettings
from slow_thinker_ii.bootstrap import load_configuration
from support.configuration import llm_models

from .configurations import EXAMPLE, local, simulated, without, written


def test_the_example_configuration_loads_from_the_working_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    configuration = load_configuration(EXAMPLE)
    assert configuration.database == tmp_path / ".local/state.sqlite3"
    assert configuration.workspace == tmp_path / ".local/runs"
    assert configuration.server.public_url == "http://127.0.0.1:8000"
    assert configuration.server.allowed_hosts == ("127.0.0.1:8000", "localhost:8000")
    assert "http://127.0.0.1:8000" in configuration.server.allowed_origins
    assert configuration.server.static_directory == tmp_path / "frontend/dist"
    assert configuration.server.operator_authentication == "token"
    components = configuration.components
    assert (components.uv, components.python) == (
        tmp_path / ".venv/bin/uv",
        tmp_path / ".venv/bin/python",
    )
    assert components.installation_root == tmp_path / ".local/components"
    assert len(components.resolutions) == 3
    assert configuration.models == llm_models()
    assert [(item.name, item.credential_env) for item in configuration.providers] == [
        ("openai", "OPENAI_API_KEY"),
        ("deepseek", "DEEPSEEK_API_KEY"),
    ]
    assert configuration.budgets == BudgetLimits(1_000_000_000, 5_000_000_000)
    assert configuration.runtime.runs == RunSettings(4, 300)
    assert configuration.runtime.host_startup_seconds == 20
    assert dict(configuration.replies) == {}


def test_absolute_paths_are_kept_and_runtime_defaults_apply(tmp_path: Path) -> None:
    document = without(local(tmp_path), ("runtime",))
    configuration = load_configuration(written(tmp_path, document))
    assert configuration.database == tmp_path / "state.sqlite3"
    assert configuration.server.static_directory is None
    assert configuration.components.resolutions == ()
    assert configuration.runtime.runs == RunSettings()
    assert configuration.runtime.host_startup_seconds == 20


def test_a_public_url_loses_its_trailing_slash(tmp_path: Path) -> None:
    document = local(tmp_path, "https://slow-thinker.example:8443/")
    configuration = load_configuration(written(tmp_path, document))
    assert configuration.server.public_url == "https://slow-thinker.example:8443"


def test_simulated_models_need_no_endpoint_and_may_script_their_replies(tmp_path: Path) -> None:
    replies = {"deepseek/deepseek-flash": ['{"score": 5}', '{"score": 8}']}
    configuration = load_configuration(written(tmp_path, simulated(local(tmp_path), replies)))
    assert configuration.providers == ()
    assert dict(configuration.replies) == {
        "deepseek/deepseek-flash": ('{"score": 5}', '{"score": 8}')
    }
    assert [model.settings.provider for model in configuration.models] == ["simulated"] * 2
    assert [model.tariff for model in configuration.models] == [
        model.tariff for model in llm_models()
    ]
