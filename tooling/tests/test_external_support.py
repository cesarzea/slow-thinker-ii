"""Explicit independent source builds use cached wheels or ordinary preparation."""

import runpy
import shutil
import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.installations import Resolution

from tooling.components import prepare
from tooling.tests.component_fixtures import offline_command

ROOT = Path(__file__).resolve().parents[2]


def prepare_external_installation(directory: Path) -> tuple[Path, Resolution]:
    monkeypatch = pytest.MonkeyPatch()
    if (ROOT / ".local/components/preparations").exists():
        monkeypatch.setattr(prepare, "command", cached_command)
    try:
        monkeypatch.setattr(sys, "argv", arguments(directory))
        runpy.run_module("tooling.components", run_name="__main__")
        record = next((directory / "catalog").glob("*.json"))
        resolution = Resolution.model_validate_json(record.read_text())
    finally:
        monkeypatch.undo()
    return directory, resolution


def arguments(directory: Path) -> list[str]:
    return [
        "prepare",
        "--external-project",
        str(ROOT / "examples/resource-agent"),
        "--registration",
        str(ROOT / "examples/resource-agent/registration.json"),
        "--descriptor",
        str(ROOT / "examples/resource-agent/resource-agent.component.json"),
        "--dependency-project",
        str(ROOT / "components/host"),
        "--dependency-project",
        str(ROOT / "components/llm-call"),
        "--destination",
        str(directory),
    ]


def cached_command(arguments: list[str], working: Path) -> str:
    wheels = working / "wheels"
    for source in (ROOT / ".local/components/preparations").glob("*/wheels/*.whl"):
        target = wheels / source.name
        if not target.exists():
            shutil.copyfile(source, target)
    return offline_command(arguments, working)
