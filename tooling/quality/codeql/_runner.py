"""Coordinate isolated source, database execution and retained evidence."""

from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from ._commands import run_command
from ._policy import bundled_suites, validate_languages
from ._report import validate_report
from ._snapshot import snapshot
from ._types import AnalysisResult, CodeQLFailure

RESOURCES = ("--threads=2", "--ram=4096")


def run_verification(
    root: Path, executable: Path, languages: tuple[str, ...]
) -> tuple[AnalysisResult, ...]:
    validate_languages(languages)
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise CodeQLFailure(f"Repository root is not a directory: {root}")
    base = _workspace_directory(root)
    output = base / "reports" / uuid4().hex
    output.mkdir(parents=True)
    try:
        version, suites = bundled_suites(executable.resolve(), languages, root, output)
        with TemporaryDirectory(prefix="run-", dir=base / "scratch") as temporary:
            scratch = Path(temporary)
            sources = snapshot(root, scratch / "source", languages, output)
            return tuple(
                _analyze(
                    root,
                    executable.resolve(),
                    scratch,
                    output,
                    language,
                    suites[language],
                    version,
                    sources[language],
                )
                for language in languages
            )
    except (CodeQLFailure, OSError, UnicodeError, ValueError) as error:
        raise CodeQLFailure(f"{error}; retained evidence: {output}") from error


def _workspace_directory(root: Path) -> Path:
    directory = root
    for name in (".local", "verification", "codeql"):
        directory /= name
        if directory.is_symlink():
            raise CodeQLFailure(f"Verification directory cannot be a symlink: {directory}")
        directory.mkdir(exist_ok=True)
    for name in ("scratch", "reports"):
        child = directory / name
        if child.is_symlink():
            raise CodeQLFailure(f"Verification directory cannot be a symlink: {child}")
        child.mkdir(exist_ok=True)
    return directory


def _analyze(
    root: Path,
    executable: Path,
    scratch: Path,
    output: Path,
    language: str,
    suite: Path,
    version: str,
    owned: frozenset[str],
) -> AnalysisResult:
    database = scratch / f"{language}-database"
    run_command(
        _create_arguments(executable, database, scratch / "source", language),
        root,
        output / f"{language}-create.log",
    )
    report = output / f"{language}.sarif"
    run_command(
        _analysis_arguments(executable, database, suite, report),
        root,
        output / f"{language}-analyze.log",
    )
    return validate_report(report, language, version, owned)


def _create_arguments(
    executable: Path, database: Path, source: Path, language: str
) -> tuple[str, ...]:
    return (
        str(executable),
        "database",
        "create",
        str(database),
        f"--language={language}",
        f"--source-root={source}",
        "--build-mode=none",
        *RESOURCES,
    )


def _analysis_arguments(
    executable: Path, database: Path, suite: Path, report: Path
) -> tuple[str, ...]:
    return (
        str(executable),
        "database",
        "analyze",
        str(database),
        str(suite),
        "--format=sarifv2.1.0",
        f"--output={report}",
        "--no-download",
        "--no-sarif-group-rules-by-pack",
        *RESOURCES,
    )
