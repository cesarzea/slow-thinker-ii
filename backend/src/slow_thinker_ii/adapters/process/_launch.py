"""Trusted launch data; graphs never supply executable paths or argument vectors."""

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from ._secrets import ProcessSecret, secret_environment


@dataclass(frozen=True)
class ProcessLaunch:
    python: Path
    module: str
    bootstrap: Path
    workspace: Path
    startup_seconds: float
    shutdown_seconds: float
    max_message_bytes: int
    secrets: tuple[ProcessSecret, ...] = field(default=(), repr=False)

    def __post_init__(self) -> None:
        secret_environment(self.secrets)
        if not all(path.is_absolute() for path in (self.python, self.bootstrap, self.workspace)):
            raise ValueError("Launch paths must be absolute")
        if not re.fullmatch(r"[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*", self.module):
            raise ValueError("Invalid installed module name")
        for seconds in (self.startup_seconds, self.shutdown_seconds):
            if not math.isfinite(seconds) or seconds <= 0:
                raise ValueError("Process timeouts must be finite and positive")
        if self.max_message_bytes < 1:
            raise ValueError("Protocol frames need a positive byte limit")
