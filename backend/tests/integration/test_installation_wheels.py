"""A correct archive hash cannot excuse mismatched distribution metadata."""

from pathlib import Path
from zipfile import ZipFile

import pytest
from slow_thinker_ii.adapters.installations import ComponentRegistration
from support.installations import new_catalog
from support.wheels import lockfile, wheel

REGISTRATION = ComponentRegistration(
    type_id="test.agent",
    type_version="1",
    distribution="sample-agent",
    version="1.0",
    entry_point="sample_agent:Agent",
)


def replace_metadata(artifact: Path, old: bytes, new: bytes) -> None:
    with ZipFile(artifact) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    with ZipFile(artifact, "w") as archive:
        for name, content in files.items():
            archive.writestr(
                name, content.replace(old, new) if name.endswith("/METADATA") else content
            )


@pytest.mark.parametrize(
    "old,new,diagnostic",
    [
        (b"Name: sample-agent", b"Name: another-agent", "distribution does not match"),
        (b"Version: 1.0", b"Version: 2.0", "version does not match"),
    ],
)
def test_wheel_metadata_must_match_identity(
    tmp_path: Path,
    old: bytes,
    new: bytes,
    diagnostic: str,
) -> None:
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent: pass\n")
    replace_metadata(artifact, old, new)
    with pytest.raises(ValueError, match=diagnostic):
        new_catalog(tmp_path).prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    assert not (tmp_path / "installations/catalog").exists()


def test_multiple_metadata_files_are_rejected(tmp_path: Path) -> None:
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent: pass\n")
    with ZipFile(artifact, "a") as archive:
        archive.writestr("other-1.0.dist-info/METADATA", "Name: other\nVersion: 1.0\n")
    with pytest.raises(ValueError, match="one distribution metadata"):
        new_catalog(tmp_path).prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)


def test_missing_compatible_wheel_fails_before_creating_environment(tmp_path: Path) -> None:
    artifact = wheel(tmp_path, "sample-agent", "1.0", "class Agent: pass\n")
    lock = lockfile(tmp_path, (artifact,))
    artifact.rename(artifact.with_name(artifact.name.replace("py3-none-any", "py2-none-any")))
    with pytest.raises(ValueError, match="one compatible regular wheel"):
        new_catalog(tmp_path).prepare(lock, tmp_path, REGISTRATION)
    assert not (tmp_path / "installations/resolutions").exists()
