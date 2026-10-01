"""Public contracts for reproducible CodeQL verification."""

from pathlib import Path

from ._runner import run_verification
from ._types import AnalysisResult as AnalysisResult
from ._types import CodeQLFailure as CodeQLFailure


def verify_codeql(
    root: Path, executable: Path, languages: tuple[str, ...] = ("python", "javascript")
) -> tuple[AnalysisResult, ...]:
    """Verify current owned source; raise CodeQLFailure on any rejected gate."""
    try:
        return run_verification(root, executable, languages)
    except (OSError, UnicodeError, ValueError) as error:
        raise CodeQLFailure(f"CodeQL verification failed: {error}") from error
