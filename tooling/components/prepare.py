"""Resolve production dependencies, retain their wheels, then install strictly offline."""

from pathlib import Path
from uuid import uuid4

from slow_thinker_ii.adapters.installations import (
    InstallationCatalog,
    Resolution,
)

from tooling.components.artifacts import record_provenance, write_inputs
from tooling.components.build import build_wheels, command, verify_built_wheels, wheel_hashes
from tooling.components.selector import with_selector
from tooling.components.targets import PreparationTarget, target

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
    root: Path,
    destination: Path,
    uv: Path,
    python: Path,
    name: str,
    *,
    selector_project: Path | None = None,
) -> Resolution:
    recipe = _recipe(name, selector_project)
    return prepare_recipe(root, destination, uv, python, recipe)


def prepare_recipe(
    root: Path,
    destination: Path,
    uv: Path,
    python: Path,
    recipe: PreparationTarget,
    metadata: dict[str, str] | None = None,
) -> Resolution:
    preparation = destination / "preparations" / uuid4().hex
    wheels = preparation / "wheels"
    wheels.mkdir(parents=True, exist_ok=False)
    sources = build_wheels(tuple(root / path for path in recipe.projects), wheels, python)
    built = wheel_hashes(wheels)
    inputs = write_inputs(recipe, preparation)
    lock = preparation / "requirements.txt"
    resolve_and_fetch(uv, python, inputs, lock, wheels)
    verify_built_wheels(wheels, built)
    provenance = record_provenance(sources, built, uv, preparation, metadata)
    catalog = InstallationCatalog(destination, uv, python)
    return catalog.prepare(lock, wheels, recipe.registration, provenance)


def _recipe(name: str, selector_project: Path | None) -> PreparationTarget:
    recipe = target(name)
    if selector_project is not None:
        if name != "redirector":
            raise ValueError("Selector projects are only valid for Redirector preparation")
        recipe = with_selector(recipe, selector_project)
    return recipe


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
