"""Owned fixture projects and a strictly local dependency index for preparation tests."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import Resolution

from tooling.components import prepare
from tooling.components.build import command


def project(
    root: Path,
    folder: str,
    module: str,
    body: str,
    dependencies: str,
    *,
    group: str = "components",
    version: str = "0.1.0.dev1",
) -> None:
    directory = root / group / folder
    package = directory / "src" / module
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(body)
    (directory / "pyproject.toml").write_text(
        '[build-system]\nrequires=["hatchling"]\nbuild-backend="hatchling.build"\n'
        f'[project]\nname="{module.replace("_", "-")}"\nversion="{version}"\n'
        f'dependencies={dependencies}\n[tool.hatch.build.targets.wheel]\npackages=["src/{module}"]\n'
    )


def offline_command(arguments: list[str], directory: Path) -> str:
    offline = list(arguments)
    for flag in ("--index-url", "--default-index"):
        if flag in offline:
            index = offline.index(flag)
            del offline[index : index + 2]
            offline.append("--no-index")
    return command(offline, directory)


def patch_preparation(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = prepare.prepare_component

    def use_fixture(
        ignored_root: Path,
        destination: Path,
        uv: Path,
        python: Path,
        name: str,
        *,
        selector_project: Path | None = None,
    ) -> Resolution:
        del ignored_root
        return original(root, destination, uv, python, name, selector_project=selector_project)

    monkeypatch.setattr(prepare, "prepare_component", use_fixture)
    monkeypatch.setattr(prepare, "command", offline_command)
