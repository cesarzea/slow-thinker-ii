"""Isolated Git and pinned-suite fixtures for the public verification gate."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

from .simulator import CommandRunner, SimulatedCodeQL

POLICY = Path(__file__).resolve().parents[2] / "quality/codeql/policy.json"


@dataclass(frozen=True)
class Gate:
    root: Path
    executable: Path
    cli: SimulatedCodeQL

    def evidence(self) -> tuple[Path, ...]:
        return tuple((self.root / ".local/verification/codeql/reports").iterdir())

    def scratch(self) -> tuple[Path, ...]:
        return tuple((self.root / ".local/verification/codeql/scratch").iterdir())


def write_file(root: Path, name: str, content: str = "owned source\n") -> Path:
    destination = root / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content)
    return destination


def git(root: Path, *arguments: str) -> None:
    subprocess.run(("git", *arguments), cwd=root, capture_output=True, text=True, check=True)


def bundle(directory: Path) -> Path:
    policy = cast(dict[str, object], json.loads(POLICY.read_text()))
    packs = cast(dict[str, str], policy["packs"])
    executable = write_file(directory, "codeql", "simulated pinned CLI\n")
    for language, version in packs.items():
        name = (
            f"qlpacks/codeql/{language}-queries/{version}/codeql-suites/"
            f"{language}-security-and-quality.qls"
        )
        write_file(directory, name, "- queries: .\n")
    return executable


@pytest.fixture
def gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Gate:
    root = tmp_path / "project"
    root.mkdir()
    git(root, "init", "-q")
    write_file(root, "source.py", "value = 'tracked version'\n")
    write_file(root, "frontend/main.ts", "export const value = 1;\n")
    write_file(root, ".gitignore", "ignored/\n")
    git(root, "add", ".")
    cli = SimulatedCodeQL(cast(CommandRunner, subprocess.run))
    executable = bundle(tmp_path / "bundle")
    monkeypatch.setattr(subprocess, "run", cli.run)
    return Gate(root, executable, cli)
