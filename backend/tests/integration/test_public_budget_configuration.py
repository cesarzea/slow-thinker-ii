"""Startup budgets cross the public boundary as exact decimal USD strings."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.preparation import EnvironmentSecrets
from slow_thinker_ii.bootstrap import load_execution_setup
from slow_thinker_ii.contracts import JsonValue, encode_json, json_object
from support.operator_http import TOKEN
from support.startup_configuration import startup_record


@pytest.mark.parametrize(
    "amount,expected", [("3.000000000", 3_000_000_000), ("0.000000001", 1), ("0", 0)]
)
def test_decimal_limits_are_exact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, amount: str, expected: int
) -> None:
    record = startup_record(tmp_path)
    limits = json_object(record["limits"])
    limits["run_budget"] = amount
    record["limits"] = limits
    path = tmp_path / "execution.json"
    path.write_text(encode_json(record))
    monkeypatch.setenv("SLOW_THINKER_TEST_OPERATOR_TOKEN", TOKEN)
    assert load_execution_setup(path).configuration.limits.run_budget == expected


@pytest.mark.parametrize(
    "amount", [-1, 3, 0.1, "-1", "nan", "0.0000000001", "overflow", "9223372037"]
)
def test_invalid_limits_fail_before_credentials(
    tmp_path: Path, amount: JsonValue, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = startup_record(tmp_path)
    limits = json_object(record["limits"])
    limits["run_budget"] = amount
    record["limits"] = limits
    path = tmp_path / "execution.json"
    path.write_text(encode_json(record))

    def forbidden(self: EnvironmentSecrets, reference: str) -> str:
        del self, reference
        pytest.fail("Invalid money reached credential resolution")

    monkeypatch.setattr(EnvironmentSecrets, "resolve", forbidden)
    with pytest.raises(ValueError, match="Invalid or unavailable"):
        load_execution_setup(path)
