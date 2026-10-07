"""Retained artifacts, the lock, installed files and inspection must still match before reuse."""

import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import InstallationCatalog, Resolution

from .catalogs import REGISTRATION, new_catalog, prepared
from .wheels import component_files, lockfile, wheel


def record_path(directory: Path, resolution: Resolution) -> Path:
    return directory / "installations/catalog" / f"{resolution.identity}.json"


@pytest.mark.parametrize(
    "target,diagnostic",
    [
        ("requirements.txt", "resolution/lock mismatch"),
        ("wheels/sample_agent-1.0-py3-none-any.whl", "Retained wheel contents changed"),
    ],
)
def test_changed_retained_inputs_prevent_reuse(
    tmp_path: Path, target: str, diagnostic: str
) -> None:
    catalog, resolution = prepared(tmp_path)
    changed = tmp_path / "installations/resolutions" / resolution.identity / target
    changed.write_bytes(changed.read_bytes() + b"changed")
    with pytest.raises(ValueError, match=diagnostic):
        catalog.interpreter(resolution.identity)


def test_a_record_cannot_refer_outside_its_resolution(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    escaping = resolution.artifacts[0].model_copy(update={"filename": "../escape.whl"})
    forged = resolution.model_copy(update={"artifacts": (escaping,)})
    record_path(tmp_path, resolution).write_text(forged.model_dump_json())
    with pytest.raises(ValueError, match="inside the resolution"):
        catalog.verify(resolution.identity)


def test_a_record_with_other_inspection_evidence_is_refused(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    evidence = resolution.inspection.model_copy(update={"declaration": "{}"})
    forged = resolution.model_copy(update={"inspection": evidence})
    record_path(tmp_path, resolution).write_text(forged.model_dump_json())
    with pytest.raises(ValueError, match="inspection changed"):
        catalog.verify(resolution.identity)


def test_records_of_another_identity_are_refused(tmp_path: Path) -> None:
    catalog, resolution = prepared(tmp_path)
    other = "f" * 32
    record_path(tmp_path, resolution).rename(tmp_path / "installations/catalog" / f"{other}.json")
    with pytest.raises(ValueError, match="resolution/lock mismatch"):
        catalog.verify(other)


def test_invalid_paths_identities_and_unregistered_packages_are_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="absolute root"):
        InstallationCatalog(Path("relative"), Path(sys.executable), Path(sys.executable))
    with pytest.raises(ValueError, match="absolute paths"):
        InstallationCatalog(tmp_path, Path("uv"), Path(sys.executable))
    catalog = new_catalog(tmp_path)
    for identity in ("../escape", "A" * 32, "a" * 31):
        with pytest.raises(ValueError, match="Invalid installation identity"):
            catalog.verify(identity)
    artifact = wheel(tmp_path, "other", "1.0", component_files("other"))
    with pytest.raises(ValueError, match="missing from the lock"):
        catalog.prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
