"""Launch credentials cannot alter the execution environment or appear in diagnostics."""

import sys
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.process import ProcessLaunch, ProcessSecret


@pytest.mark.parametrize(
    "name",
    ["PATH", "PYTHONPATH", "OPENAI_API_KEY", "SLOW_THINKER_SECRET_", "SLOW_THINKER_SECRET_x"],
)
def test_only_explicit_managed_secret_names_are_accepted(name: str) -> None:
    with pytest.raises(ValueError):
        ProcessSecret(name, "fixture-secret")


@pytest.mark.parametrize("value", ["", "has\x00nul"])
def test_secret_values_must_be_valid_environment_values(value: str) -> None:
    with pytest.raises(ValueError):
        ProcessSecret("SLOW_THINKER_SECRET_OPENAI", value)


def test_credentials_are_not_repr_visible_and_duplicate_names_are_rejected(tmp_path: Path) -> None:
    secret = ProcessSecret("SLOW_THINKER_SECRET_OPENAI", "fixture-secret")
    launch = ProcessLaunch(
        Path(sys.executable), "fixture", tmp_path / "config", tmp_path, 1, 1, 1000, (secret,)
    )
    assert "fixture-secret" not in repr(secret) and "fixture-secret" not in repr(launch)
    with pytest.raises(ValueError, match="Duplicate"):
        ProcessLaunch(
            Path(sys.executable),
            "fixture",
            tmp_path / "config",
            tmp_path,
            1,
            1,
            1000,
            (secret, secret),
        )
