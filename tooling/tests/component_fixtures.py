"""Owned fixture projects and a strictly local dependency index for preparation tests."""

from pathlib import Path

from tooling.components.build import command


def project(
    root: Path, folder: str, module: str, body: str, dependencies: str, *, group: str = "components"
) -> None:
    directory = root / group / folder
    package = directory / "src" / module
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(body)
    (directory / "pyproject.toml").write_text(
        '[build-system]\nrequires=["hatchling"]\nbuild-backend="hatchling.build"\n'
        f'[project]\nname="{module.replace("_", "-")}"\nversion="0.1.0.dev1"\n'
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
