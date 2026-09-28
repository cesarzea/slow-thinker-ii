"""Build identified first-party sources with the locked development toolchain."""

import hashlib
import os
import subprocess
from pathlib import Path


def command(arguments: list[str], directory: Path) -> str:
    result = subprocess.run(
        arguments,
        cwd=directory,
        env={
            "PATH": str(Path(arguments[0]).parent),
            "PIP_CONFIG_FILE": os.devnull,
            "SOURCE_DATE_EPOCH": "315532800",
        },
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Artifact preparation failed: {result.stderr[-4096:]}")
    return result.stdout


def source_hash(project: Path) -> str:
    paths = [project / "pyproject.toml"]
    paths.extend(
        path
        for path in (project / "src").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(project).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def build_wheels(projects: tuple[Path, ...], wheels: Path, python: Path) -> dict[str, str]:
    sources: dict[str, str] = {}
    for project in projects:
        checksum = source_hash(project)
        command(
            [str(python), "-B", "-I", "-m", "hatchling", "build", "-t", "wheel", "-d", str(wheels)],
            project,
        )
        if source_hash(project) != checksum:
            raise ValueError("Component source changed during the wheel build")
        sources[project.name] = checksum
    return sources


def wheel_hashes(directory: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in directory.glob("*.whl")
    }


def verify_built_wheels(directory: Path, expected: dict[str, str]) -> None:
    actual = wheel_hashes(directory)
    if any(actual.get(name) != checksum for name, checksum in expected.items()):
        raise ValueError("Dependency preparation replaced a first-party wheel")
