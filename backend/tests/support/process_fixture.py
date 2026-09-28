"""Launch the real transport against controlled, isolated test subprocesses."""

import os
import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessLaunch
from slow_thinker_ii.contracts import OperationContract

CONTRACT = OperationContract("wait", '{"type":"object"}', '{"type":"object"}')


def fixture_process(
    directory: Path,
    mode: str = "normal",
    contracts: tuple[OperationContract, ...] = (CONTRACT,),
    frame_limit: int = 1_048_576,
) -> ComponentProcess:
    bootstrap = directory / "mode"
    bootstrap.write_text(mode)
    entry = Path(__file__).with_name("component_fixture.py")
    launcher = directory / "python-fixture"
    launcher.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, '-I', {str(entry)!r}, sys.argv[-1]])\n"
    )
    launcher.chmod(0o700)
    return ComponentProcess(
        ProcessLaunch(launcher, "fixture", bootstrap, directory, 2, 0.9, frame_limit),
        contracts,
    )


def assert_reaped(process: ComponentProcess, *, forced: bool) -> None:
    outcome = process.outcome()
    assert outcome is not None and outcome.returncode is not None
    assert outcome.forced == forced
    with pytest.raises(ProcessLookupError):
        os.kill(outcome.pid, 0)
