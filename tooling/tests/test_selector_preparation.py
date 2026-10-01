"""Explicit user selector projects enter a hashed offline production closure."""

import runpy
import sys
from pathlib import Path

import pytest

from tooling.components import prepare
from tooling.components.selector import with_selector
from tooling.components.targets import target
from tooling.tests.component_fixtures import offline_command, project


def selector_projects(tmp_path: Path) -> None:
    project(tmp_path, "host", "slow_thinker_host", "class Host: pass\n", "[]")
    project(
        tmp_path,
        "redirector",
        "slow_thinker_redirector",
        "class RedirectorHost: pass\n",
        '["slow-thinker-host==0.1.0.dev1"]',
        version="0.1.0",
    )
    project(
        tmp_path, "rules", "user_rules", "def choose(value): return 'accept'\n", "[]", version="2.0"
    )


def test_custom_selector_is_an_exact_additional_distribution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    selector_projects(tmp_path)
    monkeypatch.setattr(prepare, "command", offline_command)
    python = Path(sys.executable)
    record = prepare.prepare_component(
        tmp_path,
        tmp_path / "installed",
        python.with_name("uv"),
        python,
        "redirector",
        selector_project=tmp_path / "components/rules",
    )
    assert record.inspection.packages == {
        "slow-thinker-host": "0.1.0.dev1",
        "slow-thinker-redirector": "0.1.0",
        "user-rules": "2.0",
    }
    assert record.provenance["source.rules"]
    locks = list((tmp_path / "installed/preparations").glob("*/requirements.txt"))
    assert "user-rules==2.0" in locks[0].read_text() and "--hash=sha256:" in locks[0].read_text()


@pytest.mark.parametrize(
    "metadata",
    [
        '[project]\nname="rules"\nversion="1"',
        '[build-system]\nbuild-backend="setuptools.build_meta"',
        '[build-system]\nbuild-backend="hatchling.build"',
        '[build-system]\nbuild-backend="hatchling.build"\n[project]\nname=""\nversion="1"',
        '[build-system]\nbuild-backend="hatchling.build"\n[project]\nname="rules"',
        '[build-system]\nbuild-backend="hatchling.build"\n[project]\nname="slow_thinker_host"\nversion="1"',
        '[build-system]\nbuild-backend="hatchling.build"\n[project]\nname="rules"\nversion="1"',
    ],
)
def test_invalid_custom_project_is_rejected_before_build(tmp_path: Path, metadata: str) -> None:
    (tmp_path / "pyproject.toml").write_text(metadata)
    with pytest.raises(ValueError):
        with_selector(target("redirector"), tmp_path)


def test_selector_project_cannot_change_unrelated_component(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="only valid"):
        prepare.prepare_component(
            tmp_path,
            tmp_path / "installed",
            Path("uv"),
            Path(sys.executable),
            "sequence",
            selector_project=tmp_path,
        )
    assert not (tmp_path / "installed").exists()


def test_cli_rejects_selector_for_other_component(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys, "argv", ["prepare", "--component", "sequence", "--selector-project", "/tmp/rules"]
    )
    with pytest.raises(SystemExit) as captured:
        runpy.run_module("tooling.components", run_name="__main__")
    assert captured.value.code == 2
