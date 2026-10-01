"""Offline installation commands use explicit tools and a minimal environment."""

import subprocess
from pathlib import Path

UV_VERSION = "uv 0.12.19"


def run(arguments: list[str], directory: Path, timeout: float = 120) -> str:
    result = subprocess.run(
        arguments,
        cwd=directory,
        env={"PATH": str(Path(arguments[0]).parent)},
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(f"Installation command failed: {result.stderr[-4096:]}")
    if len(result.stdout) > 1_048_576:
        raise ValueError("Installation inspection output exceeds its limit")
    return result.stdout


class OfflineInstaller:
    def __init__(self, uv: Path, python: Path) -> None:
        if not uv.is_absolute() or not python.is_absolute():
            raise ValueError("Installation tools must use absolute paths")
        self.uv, self.python = uv, python

    def command(self, directory: Path, *arguments: str) -> str:
        return run(
            [
                str(self.uv),
                "--no-config",
                "--offline",
                "--no-cache",
                "--no-python-downloads",
                *arguments,
            ],
            directory,
        )

    def install(self, directory: Path) -> Path:
        if run([str(self.uv), "--version"], directory).split()[:2] != UV_VERSION.split():
            raise ValueError("The installation tool version does not match")
        environment = directory / "environment"
        self.command(directory, "venv", "--python", str(self.python), str(environment))
        python = environment / "bin/python"
        self.command(
            directory,
            "pip",
            "sync",
            "--python",
            str(python),
            "--no-index",
            "--find-links",
            str(directory / "wheels"),
            "--require-hashes",
            "--only-binary",
            ":all:",
            "--link-mode",
            "copy",
            str(directory / "requirements.txt"),
        )
        self.command(directory, "pip", "check", "--python", str(python))
        return python
