"""The use cases the HTTP adapter serves and the settings that guard them."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from slow_thinker_ii.application import (
    GraphLibrary,
    LlmGateway,
    ReportService,
    RunService,
    UsageService,
)
from slow_thinker_ii.catalog import Catalog

_TOKEN = re.compile(r"[!-~]{32,128}")  # visible ASCII, safe in an Authorization header
_HOST = re.compile(r"[!-~]+")


@dataclass(frozen=True)
class HttpServices:
    """The use cases behind the routes; every route calls them on the event-loop thread."""

    catalog: Callable[[], Catalog]
    graphs: GraphLibrary
    runs: RunService
    gateway: LlmGateway
    reports: ReportService
    usage: UsageService


@dataclass(frozen=True)
class HttpSettings:
    """Operator access, request bounds and the optional compiled interface.

    Raises `ValueError` with an English message for invalid settings; the token never appears
    in messages or in `repr`.
    """

    operator_token: str | None = field(repr=False)  # None: no operator authentication (opt-in)
    allowed_hosts: tuple[str, ...]  # exact Host header values, e.g. "127.0.0.1:8000"
    allowed_origins: tuple[str, ...]  # exact browser origins, e.g. "http://127.0.0.1:5173"
    max_body_bytes: int = 1_048_576
    static_directory: Path | None = None  # compiled interface, served at "/"

    def __post_init__(self) -> None:
        token = self.operator_token
        if token is not None and _TOKEN.fullmatch(token) is None:
            raise ValueError(
                "The operator token must be 32 to 128 visible ASCII characters without spaces."
            )
        if not self.allowed_hosts or not all(_HOST.fullmatch(host) for host in self.allowed_hosts):
            raise ValueError("At least one allowed host is required, each without spaces.")
        for origin in self.allowed_origins:
            _check_origin(origin)
        if type(self.max_body_bytes) is not int or self.max_body_bytes < 1:
            raise ValueError("The request body bound must be a positive number of bytes.")


def _check_origin(origin: str) -> None:
    """An origin is exactly `scheme://authority`, as browsers send it in `Origin`."""
    parts = urlsplit(origin)
    exact = f"{parts.scheme}://{parts.netloc}" == origin
    if parts.scheme not in ("http", "https") or not parts.hostname or not exact:
        raise ValueError(f"The allowed origin “{origin}” must be exactly scheme://host[:port].")
    if parts.username is not None or parts.password is not None:
        raise ValueError(f"The allowed origin “{origin}” must not contain credentials.")
