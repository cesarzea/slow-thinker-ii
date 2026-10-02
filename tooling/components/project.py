"""Static src-layout Hatchling identities for explicitly trusted source projects."""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from packaging.version import InvalidVersion, Version


@dataclass(frozen=True)
class Project:
    path: Path
    name: str
    version: str

    @property
    def requirement(self) -> str:
        return f"{self.name}=={self.version}"


def record(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("Project metadata must contain static tables")
    return cast(dict[str, object], value)


def project(path: Path) -> Project:
    location = path.resolve()
    metadata = tomllib.loads((location / "pyproject.toml").read_text(encoding="utf-8"))
    build, fields = record(metadata.get("build-system")), record(metadata.get("project"))
    if build.get("build-backend") != "hatchling.build" or "backend-path" in build:
        raise ValueError("External preparation requires the controlled Hatchling backend")
    if build.get("requires") != ["hatchling>=1.27,<2"] or fields.get("dynamic"):
        raise ValueError("External preparation requires pinned build policy and static metadata")
    name, version = fields.get("name"), fields.get("version")
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError("External project requires a static distribution name")
    if not isinstance(version, str) or not (location / "src").is_dir():
        raise ValueError("External project requires a static version and src layout")
    try:
        Version(version)
    except InvalidVersion as error:
        raise ValueError("External project has an invalid static version") from error
    return Project(location, name, version)


def closure(primary: Project, dependencies: tuple[Path, ...]) -> tuple[Project, ...]:
    projects = (primary, *(project(path) for path in dependencies))
    names = [re.sub(r"[-_.]+", "-", item.name).lower() for item in projects]
    if len(set(names)) != len(names) or len({item.path for item in projects}) != len(projects):
        raise ValueError("External dependency projects require unique identities and paths")
    return projects
