"""Every bundled target prepares production wheels and real inherited class metadata offline."""

import json
import runpy
import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import Resolution

from tooling.components import prepare
from tooling.components.targets import target
from tooling.tests.component_fixtures import offline_command, project


def projects(root: Path) -> None:
    project(root, "host", "slow_thinker_host", "class Host: pass\n", "[]")
    project(
        root,
        "llm-call",
        "slow_thinker_llm_call",
        "class LLMCall: pass\n",
        '["slow-thinker-host==0.1.0.dev1"]',
    )
    project(
        root,
        "openai-model",
        "slow_thinker_openai_model",
        "class OpenAIModelHost: pass\n",
        '["slow-thinker-host==0.1.0.dev1"]',
    )
    project(
        root,
        "grounded-review",
        "example_grounded_review",
        "from slow_thinker_llm_call import LLMCall\nclass GroundedReview(LLMCall): pass\n",
        '["slow-thinker-llm-call==0.1.0.dev1"]',
        group="examples",
    )


@pytest.mark.parametrize("name", ["llm-call", "openai-model", "grounded-review"])
def test_component_targets_use_separate_exact_production_closures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    projects(tmp_path)
    monkeypatch.setattr(prepare, "command", offline_command)
    python = Path(sys.executable)
    record = prepare.prepare_component(
        tmp_path, tmp_path / "installed", python.with_name("uv"), python, name
    )
    assert record.registration == target(name).registration
    assert "slow-thinker-ii" not in record.inspection.packages
    assert "pytest" not in record.inspection.packages
    assert record.inspection.base_entry_point == (
        "slow_thinker_llm_call:LLMCall" if name == "grounded-review" else None
    )
    assert (tmp_path / "installed/catalog" / f"{record.identity}.json").is_file()


def test_unknown_preparation_target_is_rejected_without_writing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown component"):
        prepare.prepare_component(
            tmp_path, tmp_path / "installed", Path(sys.executable), Path(sys.executable), "unknown"
        )
    assert not list(tmp_path.iterdir())


def test_all_components_cli_retains_an_explicit_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projects(tmp_path)
    project(
        tmp_path,
        "sequence",
        "slow_thinker_sequence",
        "class SequenceHost: pass\n",
        '["slow-thinker-host==0.1.0.dev1"]',
    )
    original = prepare.prepare_component

    def use_fixture(root: Path, destination: Path, uv: Path, python: Path, name: str) -> Resolution:
        del root
        return original(tmp_path, destination, uv, python, name)

    monkeypatch.setattr(prepare, "prepare_component", use_fixture)
    monkeypatch.setattr(prepare, "command", offline_command)
    destination = tmp_path / "installed"
    monkeypatch.setattr(
        sys, "argv", ["prepare", "--component", "all", "--destination", str(destination)]
    )
    runpy.run_module("tooling.components", run_name="__main__")
    assert_bundle(destination)


def assert_bundle(destination: Path) -> None:
    bundles = list((destination / "bundles").glob("*.json"))
    assert len(bundles) == 1
    record = json.loads(bundles[0].read_text())
    assert set(record["resolutions"]) == {"sequence", "llm-call", "openai-model", "grounded-review"}
    assert all(
        (destination / "catalog" / f"{identity}.json").is_file()
        for identity in record["resolutions"].values()
    )
