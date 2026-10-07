"""Exercise wheel builds, hash-locked resolution and provenance with an offline index."""

import json
import runpy
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest
from slow_thinker_ii.adapters.installations import InstallationCatalog

from tooling.components import build, prepare
from tooling.components.build import build_wheels, command, verify_built_wheels, wheel_hashes
from tooling.components.registration import Registration, read_registration
from tooling.tests.component_fixtures import (
    component_projects,
    digest,
    locked,
    offline_command,
    patch_preparation,
    project,
)


def test_prepare_builds_wheels_and_a_verifiable_hash_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    component_projects(tmp_path)
    monkeypatch.setattr(prepare, "command", offline_command)
    python = Path(sys.executable)
    record = prepare.prepare_component(
        tmp_path, tmp_path / "prepared", python.with_name("uv"), python, "llm-call"
    )
    assert record.registration == Registration(
        "llm-call", "1.0.0", "slow-thinker-llm-call", "0.1.0.dev1", "slow_thinker_llm_call"
    )
    lock = locked(record.directory / "requirements.txt")
    assert set(lock) == {"slow-thinker-host==0.1.0.dev1", "slow-thinker-llm-call==0.1.0.dev1"}
    wheels = list((record.directory / "wheels").glob("*.whl"))
    assert len(wheels) == 2
    assert all(any(digest(wheel) in hashes for hashes in lock.values()) for wheel in wheels)
    saved = json.loads((record.directory / "registration.json").read_text())
    assert saved == record.registration.record()
    assert json.loads((record.directory / "provenance.json").read_text()) == record.provenance
    assert record.provenance["source.host"] and record.provenance["source.llm-call"]
    assert record.provenance["uv"].startswith("uv 0.12.19")


@pytest.mark.parametrize("entry_point", [False, True])
def test_a_component_wheel_must_ship_its_declaration_and_entry_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, entry_point: bool
) -> None:
    project(tmp_path, "host", "slow_thinker_host")
    project(tmp_path, "router", "slow_thinker_router", '["slow-thinker-host==0.1.0.dev1"]')
    package = tmp_path / "components/router/src/slow_thinker_router"
    if entry_point:
        (package / "component.json").write_text('{"format": "slow-thinker.component/1"}')
    monkeypatch.setattr(prepare, "command", offline_command)
    python = Path(sys.executable)
    with pytest.raises(ValueError, match="entry point" if entry_point else "shipping"):
        prepare.prepare_component(
            tmp_path, tmp_path / "out", python.with_name("uv"), python, "router"
        )


@pytest.mark.parametrize(
    ("declaration", "reason"),
    [
        ("[]", "must be a JSON object"),
        ('{"format": "slow-thinker.component/2"}', "must have format"),
        ('{"format": "slow-thinker.component/1", "type": 1}', "must name its type and version"),
    ],
)
def test_registration_requires_a_component_declaration(
    tmp_path: Path, declaration: str, reason: str
) -> None:
    with ZipFile(tmp_path / "fixture-1.0-py3-none-any.whl", "w") as archive:
        archive.writestr("fixture/component.json", declaration)
        archive.writestr("fixture/__main__.py", "")
        archive.writestr("fixture-1.0.dist-info/METADATA", "Name: fixture\nVersion: 1.0\n")
    with pytest.raises(ValueError, match=reason):
        read_registration(tmp_path, "fixture")


def test_builds_require_unique_projects_and_unchanged_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project(tmp_path, "host", "slow_thinker_host")
    source, python = tmp_path / "components/host", Path(sys.executable)

    def skip(arguments: list[str], directory: Path) -> str:
        del arguments, directory
        return ""

    def rewrite(arguments: list[str], directory: Path) -> str:
        (directory / "src/slow_thinker_host/__init__.py").write_text("changed = True\n")
        return skip(arguments, directory)

    monkeypatch.setattr(build, "command", skip)
    with pytest.raises(ValueError, match="must be unique"):
        build_wheels((source, tmp_path / "copy/host"), tmp_path, python)
    monkeypatch.setattr(build, "command", rewrite)
    with pytest.raises(ValueError, match="source changed during the wheel build"):
        build_wheels((source,), tmp_path, python)


def test_build_failure_has_a_bounded_diagnostic(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Artifact preparation failed"):
        command([sys.executable, "-I", "-c", "raise ValueError('failed fixture')"], tmp_path)


def test_dependency_fetch_cannot_replace_built_wheels(tmp_path: Path) -> None:
    artifact = tmp_path / "test.whl"
    artifact.write_bytes(b"original artifact")
    built = wheel_hashes(tmp_path)
    artifact.write_bytes(b"changed artifact")
    with pytest.raises(ValueError, match="replaced a first-party wheel"):
        verify_built_wheels(tmp_path, built)


def test_the_cli_installs_into_the_requested_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    component_projects(tmp_path)
    patch_preparation(tmp_path, monkeypatch)
    destination = tmp_path / "requested"
    arguments = ["prepare", "--component", "router", "--destination", str(destination)]
    monkeypatch.setattr(sys, "argv", arguments)
    runpy.run_module("tooling.components", run_name="__main__")
    output = capsys.readouterr().out.splitlines()
    installed = "Installed router@1.0.0 (slow-thinker-router 0.1.0.dev1): "
    (identity,) = [line.removeprefix(installed) for line in output if line.startswith(installed)]
    assert output[-1] == f'Put these identities into components.resolutions: ["{identity}"]'
    python = Path(sys.executable)
    catalog = InstallationCatalog(destination, python.with_name("uv"), python)
    resolution = catalog.verify(identity)
    assert resolution.registration.module == "slow_thinker_router"
    assert resolution.provenance["source.router"]


def test_missing_installer_is_reported_before_preparation(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_tool(_name: str) -> None:
        return None

    monkeypatch.setattr(shutil, "which", missing_tool)
    monkeypatch.setattr(sys, "argv", ["prepare"])
    with pytest.raises(RuntimeError, match="pinned uv executable"):
        runpy.run_module("tooling.components", run_name="__main__")
