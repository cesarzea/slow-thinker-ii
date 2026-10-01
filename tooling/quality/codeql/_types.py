"""Shared values within the CodeQL package."""

from dataclasses import dataclass
from pathlib import Path


class CodeQLFailure(RuntimeError):
    """Mandatory analysis failed or was incomplete."""


@dataclass(frozen=True)
class AnalysisResult:
    language: str
    notes: int
    warnings: int
    errors: int
    report: Path
