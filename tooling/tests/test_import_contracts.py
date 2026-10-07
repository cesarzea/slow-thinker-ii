"""Exercise the real architectural rules on an isolated copy of owned source."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FRAMEWORK = "Domain and engine have no framework dependencies BROKEN"
DIRECTION = "All backend capabilities follow the dependency direction BROKEN"


@pytest.mark.parametrize(
    "path, addition, diagnostic",
    [
        ("accounting/__init__.py", "import fastapi", FRAMEWORK),
        ("graphs/__init__.py", "import sqlite3", FRAMEWORK),
        ("engine/__init__.py", "import httpx", FRAMEWORK),
        ("application/__init__.py", "import pydantic", FRAMEWORK),
        ("graphs/__init__.py", "import slow_thinker_ii.engine", DIRECTION),
        ("catalog/__init__.py", "import slow_thinker_ii.graphs", DIRECTION),
        ("application/__init__.py", "import slow_thinker_ii.adapters", DIRECTION),
        (
            "catalog/__init__.py",
            "from slow_thinker_ii.accounting import _probe",
            "accounting internals are private BROKEN",
        ),
        (
            "adapters/http/__init__.py",
            "import slow_thinker_ii.adapters.sqlite",
            "Adapters are independent BROKEN",
        ),
        (
            "application/__init__.py",
            "import slow_thinker_llm_call",
            "Backend never imports component implementations BROKEN",
        ),
    ],
)
def test_import_contract_rejects(tmp_path: Path, path: str, addition: str, diagnostic: str) -> None:
    source = tmp_path / "src"
    shutil.copytree(ROOT / "backend/src", source, ignore=shutil.ignore_patterns("__pycache__"))
    (source / "slow_thinker_ii/accounting/_probe.py").write_text('"""Private probe."""\n')
    target = source / "slow_thinker_ii" / path
    target.write_text(target.read_text() + f"\n{addition}\n")
    environment = dict(os.environ, PYTHONPATH=str(source))
    result = subprocess.run(
        [
            str(Path(sys.executable).parent / "lint-imports"),
            "--config",
            str(ROOT / "pyproject.toml"),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert diagnostic in result.stdout
