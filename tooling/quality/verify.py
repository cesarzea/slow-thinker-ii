"""Run the same mandatory local and CI checks, failing on missing tools."""

import shutil
import subprocess
import sys
from pathlib import Path

from tooling.quality.coverage_gate import require_coverage
from tooling.quality.documentation import check_documentation
from tooling.quality.inventory import read_locations
from tooling.quality.source_rules import check_source

ROOT = Path(__file__).resolve().parents[2]
COMMANDS = (
    ("uv", "run", "--locked", "ruff", "check", "backend", "components", "examples", "tooling"),
    (
        "uv",
        "run",
        "--locked",
        "ruff",
        "format",
        "--check",
        "backend",
        "components",
        "examples",
        "tooling",
    ),
    ("npx", "--no-install", "pyright"),
    ("uv", "run", "--locked", "mypy"),
    ("uv", "run", "--locked", "lint-imports"),
    ("uv", "run", "--locked", "vulture"),
    ("npm", "run", "typecheck"),
    ("npm", "run", "lint"),
    ("npm", "run", "format:check"),
    ("npm", "run", "boundaries"),
    ("npm", "run", "deadcode"),
    ("uv", "run", "--locked", "python", "-m", "tooling.quality.codeql"),
    ("uv", "run", "--locked", "pytest", "--cov", "--cov-report=json:coverage/python.json"),
    ("npm", "test"),
    ("npm", "run", "build"),
    ("npm", "run", "test:e2e"),
    (
        "uv",
        "run",
        "--locked",
        "--directory",
        "backend",
        "--project",
        "..",
        "mutmut",
        "run",
        "slow_thinker_ii.accounting.*",
        "--max-children",
        "4",
    ),
)


def main() -> int:
    issues = check_source(ROOT, read_locations(ROOT)) + check_documentation(ROOT)
    if issues:
        sys.stderr.write("\n".join(issues) + "\n")
        return 1
    shutil.rmtree(ROOT / "backend/mutants", ignore_errors=True)
    for command in COMMANDS:
        sys.stdout.write(f"Checking: {' '.join(command)}\n")
        sys.stdout.flush()
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
    require_coverage(ROOT / "coverage/python.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
