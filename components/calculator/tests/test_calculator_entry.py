"""Calculator readiness and launch remain side-effect-free and strictly configured."""

from pathlib import Path

import pytest
from slow_thinker_calculator import CalculatorHost

from tooling.tests.test_external_entry_support import invalid_argv, invoke_entry


def test_calculator_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    invalid_argv("slow_thinker_calculator", monkeypatch)
    operations = CalculatorHost.describe({})
    assert invoke_entry("slow_thinker_calculator", {}, operations, {}, tmp_path, monkeypatch) == [
        "calculator"
    ]
    with pytest.raises(ValueError, match="client bindings"):
        invoke_entry(
            "slow_thinker_calculator", {}, operations, {"extra": {}}, tmp_path, monkeypatch
        )
