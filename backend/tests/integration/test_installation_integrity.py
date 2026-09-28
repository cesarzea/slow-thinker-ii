"""Retained artifacts, lock and runtime contents must still match before reuse."""

import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration, InstallationCatalog
from support.installations import new_catalog
from support.wheels import lockfile, wheel

REGISTRATION = ComponentRegistration(
    type_id="test.agent",
    type_version="1",
    distribution="sample-agent",
    version="1.0",
    entry_point="sample_agent:Agent",
)


@pytest.mark.parametrize(
    "target,diagnostic",
    [
        ("requirements.txt", "resolution/lock mismatch"),
        ("wheel", "Retained wheel contents changed"),
    ],
)
def test_changed_retained_input_prevents_reuse(
    tmp_path: Path, target: str, diagnostic: str
) -> None:
    catalog = new_catalog(tmp_path)
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent: pass\n")
    record = catalog.prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    directory = tmp_path / "installations/resolutions" / record.identity
    changed = directory / (f"wheels/{artifact.name}" if target == "wheel" else target)
    changed.write_bytes(changed.read_bytes() + b"changed")
    with pytest.raises(ValueError, match=diagnostic):
        catalog.interpreter(record.identity)


def test_record_cannot_refer_to_an_artifact_outside_its_directory(tmp_path: Path) -> None:
    catalog = new_catalog(tmp_path)
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent: pass\n")
    record = catalog.prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    invalid = record.model_copy(
        update={
            "artifacts": (record.artifacts[0].model_copy(update={"filename": "../escape.whl"}),)
        }
    )
    path = tmp_path / "installations/catalog" / f"{record.identity}.json"
    path.write_text(invalid.model_dump_json())
    with pytest.raises(ValueError, match="inside the resolution"):
        catalog.verify(record.identity)


def test_invalid_catalog_paths_and_unregistered_package_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="absolute root"):
        InstallationCatalog(Path("relative"), Path(sys.executable), Path(sys.executable))
    with pytest.raises(ValueError, match="absolute paths"):
        InstallationCatalog(tmp_path, Path("uv"), Path(sys.executable))
    catalog = new_catalog(tmp_path)
    with pytest.raises(ValueError, match="Invalid installation identity"):
        catalog.verify("../escape")
    artifact = wheel(tmp_path, "other", "1.0", "class Agent: pass\n")
    with pytest.raises(ValueError, match="missing from the lock"):
        catalog.prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
