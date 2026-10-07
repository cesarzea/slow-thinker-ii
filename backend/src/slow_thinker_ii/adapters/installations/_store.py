"""Publish a resolution only after offline installation, inspection and declaration checks."""

import os
import shutil
from collections.abc import Mapping
from pathlib import Path
from uuid import uuid4

from packaging.utils import canonicalize_name

from slow_thinker_ii.contracts import JsonValue, json_object

from ._commands import UV_VERSION, OfflineInstaller
from ._integrity import declared, inspect_environment, inventory, require_inventory
from ._locks import read_lock
from ._records import ComponentRegistration, Resolution, WheelArtifact
from ._wheels import digest, select_wheels

PYTHON = "environment/bin/python"


class InstallationCatalog:
    """Resolutions under `<root>/resolutions/<identity>`, published in `<root>/catalog`."""

    def __init__(self, root: Path, uv: Path, python: Path) -> None:
        if not root.is_absolute():
            raise ValueError("The installation catalog needs an absolute root")
        self._root = root
        self._installer = OfflineInstaller(uv, python)

    def prepare(
        self,
        lock: Path,
        wheels: Path,
        registration: ComponentRegistration,
        provenance: Mapping[str, JsonValue] | None = None,
    ) -> Resolution:
        """Installs the hash-locked wheels offline and publishes the checked resolution."""
        text = lock.read_text()
        packages = read_lock(text)
        name = canonicalize_name(registration.distribution)
        if not any(item.name == name and item.version == registration.version for item in packages):
            raise ValueError("The registered component is missing from the lock")
        artifacts = select_wheels(wheels, packages)
        directory = self._root / "resolutions" / uuid4().hex
        _stage(directory, text, wheels, artifacts)
        self._installer.install(directory)
        resolution = _describe(directory, registration, artifacts, dict(provenance or {}))
        self._publish(directory, resolution)
        return resolution

    def verify(self, identity: str) -> Resolution:
        """The published resolution, after checking its lock, wheels, files and inspection."""
        if len(identity) != 32 or any(
            character not in "0123456789abcdef" for character in identity
        ):
            raise ValueError("Invalid installation identity")
        record = self._root / "catalog" / f"{identity}.json"
        resolution = Resolution.model_validate_json(record.read_text())
        directory = self._root / "resolutions" / identity
        if (
            resolution.identity != identity
            or digest(directory / "requirements.txt") != resolution.lock_sha256
        ):
            raise ValueError("Installation resolution/lock mismatch")
        for artifact in resolution.artifacts:
            if Path(artifact.filename).name != artifact.filename:
                raise ValueError("Artifact filename must remain inside the resolution")
            if digest(directory / "wheels" / artifact.filename) != artifact.sha256:
                raise ValueError("Retained wheel contents changed")
        if inventory(directory / "environment") != resolution.files:
            raise ValueError("Installed environment contents changed")
        inspection = inspect_environment(directory / PYTHON, resolution.registration)
        if inspection != resolution.inspection:
            raise ValueError("Installed component inspection changed")
        return resolution

    def interpreter(self, identity: str) -> Path:
        """The interpreter of a resolution's environment, verified first."""
        self.verify(identity)
        return self._root / "resolutions" / identity / PYTHON

    def _publish(self, directory: Path, resolution: Resolution) -> None:
        catalog = self._root / "catalog"
        catalog.mkdir(parents=True, exist_ok=True)
        temporary = directory / "resolution.json"
        with temporary.open("x") as stream:
            stream.write(resolution.model_dump_json(indent=2))
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, catalog / f"{resolution.identity}.json")


def _describe(
    directory: Path,
    registration: ComponentRegistration,
    artifacts: tuple[WheelArtifact, ...],
    provenance: dict[str, JsonValue],
) -> Resolution:
    inspection = inspect_environment(directory / PYTHON, registration)
    require_inventory(inspection, artifacts)
    declared(inspection, registration)
    return Resolution(
        identity=directory.name,
        registration=registration,
        uv_version=UV_VERSION,
        lock_sha256=digest(directory / "requirements.txt"),
        artifacts=artifacts,
        inspection=inspection,
        files=inventory(directory / "environment"),
        provenance=json_object(provenance),
    )


def _stage(directory: Path, lock: str, source: Path, artifacts: tuple[WheelArtifact, ...]) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "requirements.txt").write_text(lock)
    (directory / "wheels").mkdir()
    for artifact in artifacts:
        target = directory / "wheels" / artifact.filename
        shutil.copyfile(source / artifact.filename, target)
        if digest(target) != artifact.sha256:
            raise ValueError("Wheel contents changed during preparation")
