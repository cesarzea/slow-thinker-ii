"""Resolve production dependencies, retain their wheels, then install strictly offline."""

import json
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

from slow_thinker_ii.adapters.installations import (
    InstallationCatalog,
    Resolution,
)

from tooling.components.build import build_wheels, command, verify_built_wheels, wheel_hashes
from tooling.components.targets import target

RESOLVE_FLAGS = (
    "--no-config",
    "--no-cache",
    "--no-python-downloads",
    "pip",
    "compile",
    "--generate-hashes",
    "--no-header",
    "--no-annotate",
    "--only-binary",
    ":all:",
)
FETCH_FLAGS = (
    "-B",
    "-I",
    "-m",
    "pip",
    "--disable-pip-version-check",
    "download",
    "--no-cache-dir",
    "--require-hashes",
    "--only-binary=:all:",
    "--no-deps",
    "--retries",
    "0",
    "--timeout",
    "20",
)


def prepare_sequence(root: Path, destination: Path, uv: Path, python: Path) -> Resolution:
    return prepare_component(root, destination, uv, python, "sequence")


def prepare_component(
    root: Path, destination: Path, uv: Path, python: Path, name: str
) -> Resolution:
    recipe = target(name)
    preparation = destination / "preparations" / uuid4().hex
    wheels = preparation / "wheels"
    wheels.mkdir(parents=True, exist_ok=False)
    sources = build_wheels(tuple(root / path for path in recipe.projects), wheels, python)
    built = wheel_hashes(wheels)
    registration = recipe.registration
    inputs = preparation / "requirements.in"
    inputs.write_text(f"{registration.distribution}=={registration.version}\n")
    lock = preparation / "requirements.txt"
    resolve_and_fetch(uv, python, inputs, lock, wheels)
    verify_built_wheels(wheels, built)
    provenance = {
        **{f"source.{name}": checksum for name, checksum in sources.items()},
        **{f"built.{name}": checksum for name, checksum in built.items()},
        "hatchling": version("hatchling"),
        "pip": version("pip"),
        "uv": command([str(uv), "--version"], preparation).strip(),
    }
    (preparation / "provenance.json").write_text(json.dumps(provenance, indent=2))
    catalog = InstallationCatalog(destination, uv, python)
    return catalog.prepare(lock, wheels, registration, provenance)


def resolve_and_fetch(uv: Path, python: Path, inputs: Path, lock: Path, wheels: Path) -> None:
    command(
        [
            str(uv),
            *RESOLVE_FLAGS,
            str(inputs),
            "--python",
            str(python),
            "--find-links",
            str(wheels),
            "--default-index",
            "https://pypi.org/simple",
            "--output-file",
            str(lock),
        ],
        inputs.parent,
    )
    fetch_wheels(python, lock, wheels)


def fetch_wheels(python: Path, lock: Path, wheels: Path) -> None:
    command(
        [
            str(python),
            *FETCH_FLAGS,
            "--index-url",
            "https://pypi.org/simple",
            "--find-links",
            str(wheels),
            "--dest",
            str(wheels),
            "--requirement",
            str(lock),
        ],
        lock.parent,
    )
