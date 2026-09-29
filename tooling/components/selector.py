"""Explicit trusted selector-package inputs, frozen into the installation closure."""

import re
import tomllib
from pathlib import Path
from typing import cast

from tooling.components.targets import PreparationTarget


def with_selector(recipe: PreparationTarget, project: Path) -> PreparationTarget:
    location = project.resolve()
    metadata = tomllib.loads((location / "pyproject.toml").read_text(encoding="utf-8"))
    build: object = metadata.get("build-system")
    if (
        not isinstance(build, dict)
        or cast(dict[str, object], build).get("build-backend") != "hatchling.build"
    ):
        raise ValueError("Selector preparation requires the controlled Hatchling backend")
    package: object = metadata.get("project")
    if not isinstance(package, dict):
        raise ValueError("Selector project requires static Python package metadata")
    fields = cast(dict[str, object], package)
    name, version = fields.get("name"), fields.get("version")
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError("Selector project requires a static distribution name")
    if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.!+_-]*", version):
        raise ValueError("Selector project requires a static distribution version")
    normalized = re.sub(r"[-_.]+", "-", name).lower()
    if normalized in {"slow-thinker-host", "slow-thinker-redirector"}:
        raise ValueError("Selector distribution conflicts with its host or Redirector")
    if not (location / "src").is_dir():
        raise ValueError("Selector preparation requires a src-layout package")
    return PreparationTarget(
        ("components/host", "components/redirector", str(location)),
        recipe.registration,
        (f"{name}=={version}",),
    )
