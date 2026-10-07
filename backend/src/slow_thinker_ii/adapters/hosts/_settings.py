"""Launch settings of component hosts and the installed launch targets they come from."""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from slow_thinker_ii.catalog import ComponentRef


@dataclass(frozen=True)
class HostSettings:
    """Where bootstrap documents go, the platform endpoints hosts call, and process limits."""

    workspace: Path
    llm_base_url: str
    mcp_url: str
    startup_seconds: float = 20
    shutdown_seconds: float = 5
    max_message_bytes: int = 1_048_576
    max_concurrent_invocations: int = 4

    def __post_init__(self) -> None:
        if not self.workspace.is_absolute():
            raise ValueError("The host workspace must be an absolute path")
        for url in (self.llm_base_url, self.mcp_url):
            if not url.startswith(("http://", "https://")):
                raise ValueError(f"Platform endpoints must be HTTP URLs: {url!r}")
        for seconds in (self.startup_seconds, self.shutdown_seconds):
            if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError("Host timeouts must be finite and positive")
        if self.max_message_bytes < 65_536 or self.max_concurrent_invocations < 1:
            raise ValueError("Host message and concurrency limits are too small")


class LaunchTarget(Protocol):
    """The installed environment of each component; implemented by `adapters.installations`."""

    def interpreter(self, ref: ComponentRef) -> Path: ...

    def module(self, ref: ComponentRef) -> str: ...
