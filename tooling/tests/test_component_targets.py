"""Each target prepares its own closure with the host SDK; real wheels ship the contract."""

import json
import runpy
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

from tooling.components import prepare
from tooling.components.build import build_wheels
from tooling.components.registration import Registration, read_registration
from tooling.components.targets import TARGETS, PreparationTarget, target
from tooling.tests.component_fixtures import (
    component_projects,
    locked,
    offline_command,
    patch_preparation,
)

ROOT = Path(__file__).resolve().parents[2]


def test_targets_are_the_packaged_components() -> None:
    assert TARGETS == ("llm-call", "router", "memory")
    assert target("llm-call") == PreparationTarget(
        ("components/host", "components/llm-call"), "slow_thinker_llm_call"
    )


@pytest.mark.parametrize("name", TARGETS)
def test_each_target_has_an_exact_production_closure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    component_projects(tmp_path)
    monkeypatch.setattr(prepare, "command", offline_command)
    python = Path(sys.executable)
    record = prepare.prepare_component(
        tmp_path, tmp_path / "installed", python.with_name("uv"), python, name
    )
    assert (record.registration.type, record.registration.type_version) == (name, "1.0.0")
    assert set(locked(record.directory / "requirements.txt")) == {
        "slow-thinker-host==0.1.0.dev1",
        f"slow-thinker-{name}==0.1.0.dev1",
    }


def test_unknown_preparation_target_is_rejected_without_writing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown component"):
        prepare.prepare_component(
            tmp_path, tmp_path / "installed", Path(sys.executable), Path(sys.executable), "unknown"
        )
    assert not list(tmp_path.iterdir())


def test_all_components_are_installed_and_retained_in_a_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    component_projects(tmp_path)
    patch_preparation(tmp_path, monkeypatch)
    destination = tmp_path / "installed"
    monkeypatch.setattr(sys, "argv", ["prepare", "--destination", str(destination)])
    runpy.run_module("tooling.components", run_name="__main__")
    (bundle,) = (destination / "bundles").glob("*.json")
    record = json.loads(bundle.read_text())
    assert record["schema_version"] == "3" and record["installation_root"] == str(destination)
    assert set(record["components"]) == set(TARGETS)
    for name, entry in record["components"].items():
        assert entry["registration"]["type"] == name
        assert (destination / "catalog" / f"{entry['resolution']}.json").is_file()
        assert (Path(entry["preparation"]) / "requirements.txt").is_file()


@pytest.mark.parametrize("name", TARGETS)
def test_real_component_wheels_ship_the_contract_declaration(tmp_path: Path, name: str) -> None:
    recipe = target(name)
    build_wheels((ROOT / f"components/{name}",), tmp_path, Path(sys.executable))
    assert read_registration(tmp_path, recipe.module) == Registration(
        name, "1.0.0", f"slow-thinker-{name}", "0.1.0.dev1", recipe.module
    )
    (wheel,) = tmp_path.glob("*.whl")
    with ZipFile(wheel) as archive:
        shipped = json.loads(archive.read(f"{recipe.module}/component.json"))
    example = ROOT / f"docs/contracts/examples/{name}.component.json"
    assert shipped == json.loads(example.read_text(encoding="utf-8"))
