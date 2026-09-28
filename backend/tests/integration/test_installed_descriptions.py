"""Installed descriptions run in the verified interpreter without inherited credentials."""

import subprocess
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration
from support.installations import new_catalog
from support.wheels import lockfile, wheel

SOURCE = """
from types import SimpleNamespace
class Component:
    @staticmethod
    def describe(config):
        import os
        assert os.getenv("OPENAI_API_KEY") is None
        assert os.getenv("SLOW_THINKER_SECRET_OPENAI") is None
        return (SimpleNamespace(name="generate", input_schema=config["schema"],
            output_schema={"type":"object"}),)
"""


def install(directory: Path, source: str = SOURCE) -> tuple[str, Path]:
    artifact = wheel(directory, "described-component", "1.0", source)
    catalog = new_catalog(directory)
    registration = ComponentRegistration(
        type_id="test.described",
        type_version="1",
        distribution="described-component",
        version="1.0",
        entry_point="described_component:Component",
    )
    result = catalog.prepare(lockfile(directory, (artifact,)), directory, registration)
    return result.identity, catalog.interpreter(result.identity)


def test_effective_contract_is_derived_from_frozen_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    identity, _ = install(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "fixture-not-forwarded")
    monkeypatch.setenv("SLOW_THINKER_SECRET_OPENAI", "fixture-not-forwarded")
    catalog = new_catalog(tmp_path)
    first = catalog.describe(identity, '{"schema":{"type":"object","required":["first"]}}')
    second = catalog.describe(identity, '{"schema":{"type":"object","required":["second"]}}')
    assert '"first"' in first.operations[0].input_schema_json
    assert '"second"' in second.operations[0].input_schema_json
    assert first.installation_json == second.installation_json
    assert "fixture-not-forwarded" not in first.config_json + first.installation_json


@pytest.mark.parametrize(
    "expression", ["()", "[]", "(object(),)", "(op, op)", "(bad,)", "(unnamed,)", "(untyped,)"]
)
def test_invalid_installed_descriptions_cannot_be_admitted(tmp_path: Path, expression: str) -> None:
    source = (
        """from types import SimpleNamespace
class Component:
    @staticmethod
    def describe(config):
        op = SimpleNamespace(name="generate", input_schema={}, output_schema={})
        bad = SimpleNamespace(name="generate", input_schema={"type":"invalid"}, output_schema={})
        unnamed = SimpleNamespace(name="", input_schema={}, output_schema={})
        untyped = SimpleNamespace(name=123, input_schema={}, output_schema={})
        return """
        + expression
        + "\n"
    )
    identity, _ = install(tmp_path, source)
    with pytest.raises((ValueError, RuntimeError)):
        new_catalog(tmp_path).describe(identity, "{}")


def test_description_timeout_prevents_unbounded_preflight(tmp_path: Path) -> None:
    source = (
        "import time\nclass Component:\n    @staticmethod\n"
        "    def describe(config):\n        time.sleep(5)\n"
    )
    identity, _ = install(tmp_path, source)
    with pytest.raises(subprocess.TimeoutExpired):
        new_catalog(tmp_path).describe(identity, "{}", 0.05)


def test_description_side_effect_invalidates_the_environment(tmp_path: Path) -> None:
    source = SOURCE.replace(
        "        return (SimpleNamespace",
        '        from pathlib import Path\n        Path(__file__).write_text("changed")\n'
        "        return (SimpleNamespace",
    )
    identity, _ = install(tmp_path, source)
    with pytest.raises(ValueError, match="contents changed"):
        new_catalog(tmp_path).describe(identity, '{"schema":{}}')


@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan"), True])
def test_invalid_description_deadline_is_rejected(tmp_path: Path, seconds: float) -> None:
    identity, _ = install(tmp_path)
    with pytest.raises(ValueError, match="finite and positive"):
        new_catalog(tmp_path).describe(identity, '{"schema":{}}', seconds)
