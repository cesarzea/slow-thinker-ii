"""Exercise the real architectural rules on an isolated copy of owned source."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "path, addition, diagnostic",
    [
        ("accounting/_money.py", "import fastapi", "framework dependencies BROKEN"),
        ("access/_policy.py", "import openai", "framework dependencies BROKEN"),
        ("execution/_outcomes.py", "import sqlite3", "framework dependencies BROKEN"),
        (
            "application/_catalog.py",
            "from slow_thinker_ii.execution._outcomes import stopped_outcome",
            "Execution internals are private BROKEN",
        ),
        (
            "application/_catalog.py",
            "from slow_thinker_ii.access._authority import CallAuthority",
            "Access internals are private BROKEN",
        ),
        (
            "bootstrap/__init__.py",
            "from slow_thinker_llm_call._component import LLMCall",
            "LLMCall internals are private BROKEN",
        ),
        (
            "bootstrap/__init__.py",
            "from example_grounded_review._review import GroundedReview",
            "Derived example internals are private BROKEN",
        ),
        (
            "application/_catalog.py",
            "from slow_thinker_ii.accounting._money import parse_limit",
            "Accounting internals are private BROKEN",
        ),
        (
            "definitions/_graph.py",
            "import slow_thinker_ii.application",
            "dependency direction BROKEN",
        ),
        (
            "adapters/catalog/__init__.py",
            "from slow_thinker_ii.application._catalog import ExperimentCatalog",
            "Application internals are private BROKEN",
        ),
        (
            "bootstrap/__init__.py",
            "from slow_thinker_ii.application.library._service import ExperimentLibrary",
            "Library internals are private BROKEN",
        ),
        (
            "adapters/catalog/__init__.py",
            "from slow_thinker_ii.application.library._records import GraphReference",
            "Library internals are private BROKEN",
        ),
        (
            "application/_catalog.py",
            "from slow_thinker_ii.application.library._records import GraphReference",
            "Library internals are private BROKEN",
        ),
    ],
)
def test_import_contract_rejects(
    tmp_path: Path,
    path: str,
    addition: str,
    diagnostic: str,
) -> None:
    source = tmp_path / "src"
    shutil.copytree(ROOT / "backend/src", source, ignore=shutil.ignore_patterns("__pycache__"))
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
