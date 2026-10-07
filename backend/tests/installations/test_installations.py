"""Offline installation of real wheels; failed updates cannot damage published resolutions."""

import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import InstallationCatalog

from .catalogs import REGISTRATION, environment, new_catalog, prepared, sample_wheel
from .wheels import ROUTER_DECLARATION, component_files, lockfile, wheel


def test_a_published_resolution_records_its_inputs_and_evidence(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    assert (resolution.schema_version, resolution.uv_version) == ("2", "uv 0.12.19")
    assert resolution.registration == REGISTRATION
    assert resolution.provenance == {"source": "tests"}
    assert resolution.inspection.packages == {"sample-agent": "1.0"}
    assert resolution.inspection.declaration == ROUTER_DECLARATION
    assert (resolution.inspection.python, resolution.inspection.platform) != ("", "")
    assert [artifact.filename for artifact in resolution.artifacts] == [
        "sample_agent-1.0-py3-none-any.whl"
    ]
    assert not any("editable" in file for file in resolution.files)
    python = catalog.interpreter(resolution.identity)
    assert python.is_file() and python != Path(sys.executable)
    assert catalog.verify(resolution.identity) == resolution
    published = tmp_path / "installations/catalog" / f"{resolution.identity}.json"
    assert published.read_text() == resolution.model_dump_json(indent=2)


def test_a_failed_update_leaves_the_published_resolution_intact(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    artifact = tmp_path / "sample_agent-1.0-py3-none-any.whl"
    lock = tmp_path / "requirements.txt"
    artifact.write_bytes(artifact.read_bytes() + b"changed wheel contents")
    with pytest.raises(ValueError, match="hash mismatch"):
        catalog.prepare(lock, tmp_path, REGISTRATION)
    assert catalog.verify(resolution.identity) == resolution
    assert len(list((tmp_path / "installations/catalog").glob("*.json"))) == 1


def test_modified_installed_code_prevents_reuse(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    installed = environment(catalog, resolution)
    module = next(installed.glob("lib/python*/site-packages/sample_agent/__main__.py"))
    module.write_text("print('changed')\n")
    with pytest.raises(ValueError, match="environment contents changed"):
        catalog.interpreter(resolution.identity)


def test_a_missing_dependency_publishes_nothing(tmp_path: Path) -> None:
    files = component_files("sample_agent")
    artifact = wheel(tmp_path, "sample-agent", "1.0", files, ("missing-base==1.0",))
    with pytest.raises(RuntimeError, match="Installation command failed"):
        new_catalog(tmp_path).prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    assert not (tmp_path / "installations/catalog").exists()


def test_preparing_another_version_keeps_the_first(tmp_path: Path) -> None:
    catalog, first = prepared(tmp_path / "first")
    later = tmp_path / "second"
    later.mkdir()
    lock = lockfile(later, (sample_wheel(later),))
    second = catalog.prepare(lock, later, REGISTRATION)
    assert second.identity != first.identity
    assert catalog.verify(first.identity) == first and catalog.verify(second.identity) == second


def test_only_the_pinned_installer_version_installs(tmp_path: Path) -> None:
    uv = tmp_path / "tools" / "uv"
    uv.parent.mkdir()
    uv.write_text("#!/bin/sh\necho 'uv 0.0.1 (test)'\n")
    uv.chmod(0o755)
    catalog = InstallationCatalog(tmp_path / "installations", uv, Path(sys.executable))
    with pytest.raises(ValueError, match="installation tool version does not match"):
        catalog.prepare(lockfile(tmp_path, (sample_wheel(tmp_path),)), tmp_path, REGISTRATION)
    assert not (tmp_path / "installations/catalog").exists()
