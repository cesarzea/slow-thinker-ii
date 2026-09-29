"""Exercise wheel builds, real resolution and installation with an offline fixture index."""

import runpy
import shutil
import sys
from pathlib import Path

import pytest

from tooling.components import prepare
from tooling.components.build import command, verify_built_wheels, wheel_hashes
from tooling.tests.component_fixtures import offline_command, patch_preparation, project


def test_prepare_builds_production_wheels_and_publishes_verified_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project(tmp_path, "host", "slow_thinker_host", "class Host: pass\n", "[]")
    project(
        tmp_path,
        "sequence",
        "slow_thinker_sequence",
        "class SequenceHost: pass\n",
        '["slow-thinker-host==0.1.0.dev1"]',
    )
    monkeypatch.setattr(prepare, "command", offline_command)
    python = Path(sys.executable)
    record = prepare.prepare_sequence(
        tmp_path, tmp_path / "installed", python.with_name("uv"), python
    )
    assert record.inspection.packages == {
        "slow-thinker-host": "0.1.0.dev1",
        "slow-thinker-sequence": "0.1.0.dev1",
    }
    assert record.provenance["source.host"]
    assert record.provenance["source.sequence"]
    assert record.provenance["uv"].startswith("uv 0.12.17")


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


def test_preparation_cli_uses_requested_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project(tmp_path, "host", "slow_thinker_host", "class Host: pass\n", "[]")
    project(
        tmp_path,
        "sequence",
        "slow_thinker_sequence",
        "class SequenceHost: pass\n",
        '["slow-thinker-host==0.1.0.dev1"]',
    )
    patch_preparation(tmp_path, monkeypatch)
    destination = tmp_path / "requested"
    monkeypatch.setattr(sys, "argv", ["prepare", "--destination", str(destination)])
    runpy.run_module("tooling.components", run_name="__main__")
    assert len(list((destination / "catalog").glob("*.json"))) == 1


def test_missing_installer_is_reported_before_preparation(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_tool(_name: str) -> None:
        return None

    monkeypatch.setattr(shutil, "which", missing_tool)
    monkeypatch.setattr(sys, "argv", ["prepare"])
    with pytest.raises(RuntimeError, match="pinned uv executable"):
        runpy.run_module("tooling.components", run_name="__main__")
