"""Exercise installed checkers against deliberate violations, not mock statuses."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BIN = Path(sys.executable).parent


@pytest.mark.parametrize(
    "command, source, diagnostic",
    [
        (
            ("mypy", "--config-file", str(ROOT / "pyproject.toml")),
            "from typing import Any\ndef f(value: Any) -> Any:\n    return value\n",
            "Explicit",
        ),
        (("vulture",), "def unused_function():\n    return 1\n", "unused function"),
        (
            ("ruff", "check", "--config", str(ROOT / "pyproject.toml")),
            "def f(value):\n"
            + "".join(f"    if value == {i}:\n        return {i}\n" for i in range(9)),
            "C901",
        ),
    ],
)
def test_python_checker_rejects(
    tmp_path: Path,
    command: tuple[str, ...],
    source: str,
    diagnostic: str,
) -> None:
    fixture = tmp_path / "violation.py"
    fixture.write_text(source)
    result = subprocess.run(
        [str(BIN / command[0]), *command[1:], str(fixture)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert diagnostic in result.stdout + result.stderr


def test_pyright_rejects_wrong_type(tmp_path: Path) -> None:
    fixture = tmp_path / "violation.py"
    fixture.write_text("value: int = 'wrong'\n")
    result = subprocess.run(
        [str(ROOT / "node_modules/.bin/pyright"), "--project", str(ROOT), str(fixture)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "reportAssignmentType" in result.stdout
