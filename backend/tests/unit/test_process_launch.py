"""Trusted process launches still reject ambiguous paths and unbounded limits."""

import sys
from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import ProcessLaunch


@pytest.fixture
def launch(tmp_path: Path) -> ProcessLaunch:
    return ProcessLaunch(
        Path(sys.executable), "component.host", tmp_path / "data", tmp_path, 3, 1, 99
    )


@pytest.mark.parametrize("value", [0, -1, float("inf"), float("nan")])
def test_timeouts_must_be_bounded(launch: ProcessLaunch, value: float) -> None:
    with pytest.raises(ValueError, match="finite and positive"):
        replace(launch, startup_seconds=value)
    with pytest.raises(ValueError, match="finite and positive"):
        replace(launch, shutdown_seconds=value)


def test_paths_and_module_are_unambiguous(launch: ProcessLaunch) -> None:
    with pytest.raises(ValueError, match="absolute"):
        replace(launch, python=Path("python"))
    with pytest.raises(ValueError, match="absolute"):
        replace(launch, bootstrap=Path("data"))
    with pytest.raises(ValueError, match="absolute"):
        replace(launch, workspace=Path("."))
    with pytest.raises(ValueError, match="module name"):
        replace(launch, module="component; injected")
    with pytest.raises(ValueError, match="positive byte limit"):
        replace(launch, max_message_bytes=0)
