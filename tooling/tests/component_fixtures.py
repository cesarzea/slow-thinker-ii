"""Fixture component projects, a strictly local dependency index and lock inspection."""

import hashlib
import json
from pathlib import Path

import pytest

from tooling.components import prepare
from tooling.components.build import command
from tooling.components.prepare import Preparation
from tooling.components.targets import TARGETS

EXAMPLES = Path(__file__).resolve().parents[2] / "docs/contracts/examples"


def project(
    root: Path,
    folder: str,
    module: str,
    dependencies: str = "[]",
    *,
    declaration: object = None,
) -> None:
    """A src-layout Hatchling project; with `declaration`, a component with an entry point."""
    directory = root / "components" / folder
    package = directory / "src" / module
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('"""Fixture package."""\n')
    if declaration is not None:
        (package / "__main__.py").write_text('"""Fixture entry point."""\n')
        (package / "component.json").write_text(json.dumps(declaration))
    (directory / "pyproject.toml").write_text(
        '[build-system]\nrequires=["hatchling"]\nbuild-backend="hatchling.build"\n'
        f'[project]\nname="{module.replace("_", "-")}"\nversion="0.1.0.dev1"\n'
        f'dependencies={dependencies}\n[tool.hatch.build.targets.wheel]\npackages=["src/{module}"]\n'
    )


def component_projects(root: Path) -> None:
    """The host SDK and every target as minimal distributions shipping the contract's
    declarations, so that they also install and pass the installation's inspection."""
    project(root, "host", "slow_thinker_host")
    for name in TARGETS:
        example = EXAMPLES / f"{name}.component.json"
        declaration: object = json.loads(example.read_text(encoding="utf-8"))
        module = "slow_thinker_" + name.replace("-", "_")
        project(root, name, module, '["slow-thinker-host==0.1.0.dev1"]', declaration=declaration)


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
        ignored_root: Path, destination: Path, uv: Path, python: Path, name: str
    ) -> Preparation:
        del ignored_root
        return original(root, destination, uv, python, name)

    monkeypatch.setattr(prepare, "prepare_component", use_fixture)
    monkeypatch.setattr(prepare, "command", offline_command)


def locked(lock: Path) -> dict[str, frozenset[str]]:
    """Each exact requirement of a hash lock with its permitted SHA-256 digests."""
    entries: dict[str, frozenset[str]] = {}
    for line in lock.read_text().replace("\\\n", " ").splitlines():
        requirement, *hashes = line.split() or [""]
        if requirement and not requirement.startswith("#"):
            entries[requirement] = frozenset(item.removeprefix("--hash=sha256:") for item in hashes)
    return entries


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
