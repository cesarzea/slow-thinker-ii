"""A correct archive hash cannot excuse wheels whose metadata or form do not match the lock."""

from pathlib import Path
from zipfile import ZipFile

import pytest

from .catalogs import REGISTRATION, new_catalog, sample_wheel
from .wheels import lockfile


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
def test_wheel_metadata_must_match_the_lock(
    tmp_path: Path, old: bytes, new: bytes, diagnostic: str
) -> None:
    artifact = sample_wheel(tmp_path)
    replace_metadata(artifact, old, new)
    with pytest.raises(ValueError, match=diagnostic):
        new_catalog(tmp_path).prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)
    assert not (tmp_path / "installations").exists()


def test_a_wheel_with_two_metadata_files_is_refused(tmp_path: Path) -> None:
    artifact = sample_wheel(tmp_path)
    with ZipFile(artifact, "a") as archive:
        archive.writestr("other-1.0.dist-info/METADATA", "Name: other\nVersion: 1.0\n")
    with pytest.raises(ValueError, match="one distribution metadata"):
        new_catalog(tmp_path).prepare(lockfile(tmp_path, (artifact,)), tmp_path, REGISTRATION)


def test_a_missing_compatible_wheel_fails_before_any_environment(tmp_path: Path) -> None:
    artifact = sample_wheel(tmp_path)
    lock = lockfile(tmp_path, (artifact,))
    artifact.rename(artifact.with_name(artifact.name.replace("py3-none-any", "py2-none-any")))
    with pytest.raises(ValueError, match="one compatible regular wheel"):
        new_catalog(tmp_path).prepare(lock, tmp_path, REGISTRATION)
    assert not (tmp_path / "installations/resolutions").exists()


def test_a_wheel_changed_after_hashing_is_refused(tmp_path: Path) -> None:
    artifact = sample_wheel(tmp_path)
    lock = lockfile(tmp_path, (artifact,))
    artifact.write_bytes(artifact.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="Wheel hash mismatch"):
        new_catalog(tmp_path).prepare(lock, tmp_path, REGISTRATION)
