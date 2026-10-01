"""Run the same mandatory CodeQL verification locally and in CI."""

import os
import shutil
import sys
from pathlib import Path

from . import CodeQLFailure, verify_codeql
from ._policy import read_policy


def _executable(root: Path) -> Path:
    configured = os.environ.get("CODEQL_EXECUTABLE")
    if configured:
        return Path(configured).expanduser().resolve()
    version, _ = read_policy()
    cached = root / ".cache" / "codeql-bundle" / version / "codeql" / "codeql"
    if cached.is_file():
        return cached.resolve()
    available = shutil.which("codeql")
    if available is None:
        raise CodeQLFailure("CodeQL is missing; set CODEQL_EXECUTABLE to the pinned bundle CLI")
    return Path(available).resolve()


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    try:
        results = verify_codeql(root, _executable(root))
    except (CodeQLFailure, OSError) as error:
        sys.stderr.write(f"CodeQL verification failed: {error}\n")
        return 1
    for result in results:
        sys.stdout.write(
            f"CodeQL {result.language}: {result.notes} notes; report: {result.report}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
