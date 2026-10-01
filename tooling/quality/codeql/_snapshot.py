"""Copy current Git-owned files without consulting prior analysis artifacts."""

import shutil
from pathlib import Path, PurePosixPath

from ._commands import run_command
from ._exclusions import excluded
from ._types import CodeQLFailure

EXTENSIONS = {
    "python": frozenset({".py"}),
    "javascript": frozenset({".js", ".cjs", ".mjs", ".ts", ".tsx"}),
}


def snapshot(
    root: Path, destination: Path, languages: tuple[str, ...], output: Path
) -> dict[str, frozenset[str]]:
    raw = run_command(
        ("git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"),
        root,
        output / "source-inventory.log",
    )
    paths = _copy_files(root, destination, raw)
    sources = {
        language: frozenset(
            path for path in paths if PurePosixPath(path).suffix in EXTENSIONS[language]
        )
        for language in languages
    }
    for language, owned in sources.items():
        if not owned:
            raise CodeQLFailure(f"No current owned {language} source files")
    return sources


def _copy_files(root: Path, destination: Path, raw: str) -> set[str]:
    if raw and not raw.endswith("\0"):
        raise CodeQLFailure("Git inventory must contain NUL-terminated paths")
    paths: set[str] = set()
    destination.mkdir()
    for name in sorted(set(raw.split("\0")) - {""}):
        relative = _relative_path(name)
        if excluded(relative):
            continue
        source = root.joinpath(*relative.parts)
        _reject_symlinks(root, relative)
        if not source.exists():
            continue
        if not source.is_file():
            raise CodeQLFailure(f"Source is not a regular file: {name}")
        target = destination.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        paths.add(name)
    return paths


def _relative_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise CodeQLFailure(f"Invalid source-relative path: {name}")
    return path


def _reject_symlinks(root: Path, relative: PurePosixPath) -> None:
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise CodeQLFailure(f"Source symlinks are forbidden: {relative}")
