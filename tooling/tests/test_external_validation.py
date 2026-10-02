"""Bad metadata, descriptor/registration identities and CLI options fail before builds."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from tooling.components.external import external_target
from tooling.components.project import closure, project
from tooling.components.targets import target
from tooling.tests.test_external_support import ROOT


@pytest.mark.parametrize(
    "metadata",
    [
        '[project]\nname="x"\nversion="1"',
        '[build-system]\nbuild-backend="setuptools.build_meta"\n[project]\nname="x"\nversion="1"',
        '[build-system]\nbuild-backend="hatchling.build"\nrequires=["hatchling"]\n[project]\nname="x"\nversion="1"',
        '[build-system]\nbuild-backend="hatchling.build"\nrequires=["hatchling>=1.27,<2"]\n[project]\nname=""\nversion="1"',
        '[build-system]\nbuild-backend="hatchling.build"\nrequires=["hatchling>=1.27,<2"]\n[project]\nname="x"\nversion="bad"',
        '[build-system]\nbuild-backend="hatchling.build"\nrequires=["hatchling>=1.27,<2"]\n[project]\nname="x"\ndynamic=["version"]',
    ],
)
def test_invalid_static_project(tmp_path: Path, metadata: str) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "pyproject.toml").write_text(metadata)
    with pytest.raises(ValueError):
        project(tmp_path)


def test_duplicate_dependency_identity_and_recipe_versions() -> None:
    primary = project(ROOT / "components/host")
    assert primary.requirement == "slow-thinker-host==0.1.0.dev1"
    with pytest.raises(ValueError, match="unique"):
        closure(primary, (primary.path,))
    for name in ("model-provider", "calculator", "key-value-memory", "contextual-call"):
        assert target(name).registration.version == "0.1.0"


@pytest.mark.parametrize(
    "field,value",
    [
        ("type_id", "different"),
        ("descriptor", "different.component.json"),
        ("distribution", {"name": "wrong", "version": "0.1.0"}),
    ],
)
def test_mismatched_external_registration(tmp_path: Path, field: str, value: object) -> None:
    registration = json.loads((ROOT / "examples/resource-agent/registration.json").read_text())
    registration[field] = value
    path = tmp_path / "registration.json"
    path.write_text(json.dumps(registration))
    with pytest.raises(ValueError):
        external_target(
            ROOT,
            ROOT / "examples/resource-agent",
            path,
            ROOT / "examples/resource-agent/resource-agent.component.json",
        )


@pytest.mark.parametrize(
    "args",
    [
        ["--external-project", "/tmp/x"],
        ["--registration", "/tmp/r"],
        ["--descriptor", "/tmp/d"],
        ["--dependency-project", "/tmp/dependency"],
        ["--external-project", "/tmp/x", "--component", "calculator"],
        ["--external-project", "/tmp/x", "--selector-project", "/tmp/y"],
    ],
)
def test_cli_incomplete_external_inputs(monkeypatch: pytest.MonkeyPatch, args: list[str]) -> None:
    monkeypatch.setattr(sys, "argv", ["prepare", *args])
    with pytest.raises(SystemExit) as caught:
        runpy.run_module("tooling.components", run_name="__main__")
    assert caught.value.code == 2
