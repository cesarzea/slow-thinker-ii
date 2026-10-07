"""Install a preparation into the platform's installation catalog."""

from pathlib import Path

from slow_thinker_ii.adapters.installations import (
    ComponentRegistration,
    InstallationCatalog,
    Resolution,
)

from tooling.components.prepare import Preparation


def install(preparation: Preparation, root: Path, uv: Path, python: Path) -> Resolution:
    """Installs the hash-locked wheels offline and publishes the verified resolution."""
    directory = preparation.directory
    text = (directory / "registration.json").read_text(encoding="utf-8")
    registration = ComponentRegistration.model_validate_json(text)
    catalog = InstallationCatalog(root, uv, python)
    lock, wheels = directory / "requirements.txt", directory / "wheels"
    return catalog.prepare(lock, wheels, registration, preparation.provenance)
