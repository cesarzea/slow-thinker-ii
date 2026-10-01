"""Execute mandatory commands and retain their diagnostics."""

import shlex
import subprocess
from pathlib import Path

from ._types import CodeQLFailure


def run_command(arguments: tuple[str, ...], root: Path, log: Path) -> str:
    log.write_text(f"$ {shlex.join(arguments)}\n", encoding="utf-8")
    try:
        result = subprocess.run(
            arguments,
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )
    except (OSError, UnicodeError) as error:
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"Command could not complete: {error}\n")
        raise CodeQLFailure(f"Cannot execute {arguments[0]}: {error}; log: {log}") from error
    with log.open("a", encoding="utf-8") as stream:
        stream.write(result.stdout)
    if result.returncode:
        raise CodeQLFailure(f"Command failed ({result.returncode}); log: {log}")
    return result.stdout
