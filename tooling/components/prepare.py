"""Build first-party wheels, then resolve and fetch a hash-locked production closure."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from tooling.components.artifacts import record_provenance, write_inputs, write_registration
from tooling.components.build import build_wheels, command, verify_built_wheels, wheel_hashes
from tooling.components.registration import Registration, read_registration
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


@dataclass(frozen=True)
class Preparation:
    """A directory with `wheels/`, `requirements.txt`, `registration.json` and provenance."""

    directory: Path
    registration: Registration
    provenance: dict[str, str]


def prepare_component(
    root: Path, destination: Path, uv: Path, python: Path, name: str
) -> Preparation:
    recipe = target(name)
    preparation = destination / "preparations" / uuid4().hex
    wheels = preparation / "wheels"
    wheels.mkdir(parents=True, exist_ok=False)
    sources = build_wheels(tuple(root / path for path in recipe.projects), wheels, python)
    built = wheel_hashes(wheels)
    registration = read_registration(wheels, recipe.module)
    inputs = write_inputs(registration, preparation)
    resolve_and_fetch(uv, python, inputs, preparation / "requirements.txt", wheels)
    verify_built_wheels(wheels, built)
    provenance = record_provenance(sources, built, uv, preparation)
    write_registration(registration, preparation)
    return Preparation(preparation, registration, provenance)


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
