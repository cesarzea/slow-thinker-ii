"""Select compatible, hash-verified wheels and check distribution metadata."""

import hashlib
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

from packaging.tags import sys_tags
from packaging.utils import canonicalize_name, parse_wheel_filename

from ._locks import LockedPackage
from ._records import WheelArtifact


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _artifact(path: Path, package: LockedPackage) -> WheelArtifact:
    checksum = digest(path)
    if checksum not in package.hashes:
        raise ValueError(f"Wheel hash mismatch: {path.name}")
    with ZipFile(path) as archive:
        entries = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(entries) != 1:
            raise ValueError("A wheel must contain one distribution metadata file")
        metadata = BytesParser().parsebytes(archive.read(entries[0]))
    if canonicalize_name(str(metadata["Name"])) != package.name:
        raise ValueError("Wheel distribution does not match the lock")
    if str(metadata["Version"]) != package.version:
        raise ValueError("Wheel version does not match the lock")
    return WheelArtifact(
        filename=path.name, distribution=package.name, version=package.version, sha256=checksum
    )


def select_wheels(
    directory: Path, packages: tuple[LockedPackage, ...]
) -> tuple[WheelArtifact, ...]:
    supported = set(sys_tags())
    selected: list[WheelArtifact] = []
    candidates = sorted(directory.glob("*.whl"))
    for package in packages:
        matches: list[Path] = []
        for candidate in candidates:
            name, version, _, tags = parse_wheel_filename(candidate.name)
            if name == package.name and str(version) == package.version and tags & supported:
                matches.append(candidate)
        if len(matches) != 1 or matches[0].is_symlink():
            raise ValueError(f"Expected one compatible regular wheel for {package.name}")
        selected.append(_artifact(matches[0], package))
    return tuple(selected)
