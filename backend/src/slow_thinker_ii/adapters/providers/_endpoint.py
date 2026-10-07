"""Reviewed provider origins and credentials; authentication never comes from a request."""

import math
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal
from urllib.parse import urlsplit

REVIEWED_ORIGINS = MappingProxyType(
    {"openai": "https://api.openai.com/v1", "deepseek": "https://api.deepseek.com"}
)
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1"})


@dataclass(frozen=True)
class ProviderEndpoint:
    """Where and how one provider is called. Error messages never repeat the URL or the key."""

    provider: Literal["openai", "deepseek"]
    base_url: str  # exact reviewed origin, or an explicit loopback `/v1` URL for tests
    api_key: str = field(repr=False)
    timeout_seconds: float = 120
    max_response_bytes: int = 524_288

    def __post_init__(self) -> None:
        _check_origin(self.provider, self.base_url)
        if not self.api_key or any(not 33 <= ord(char) <= 126 for char in self.api_key):
            raise ValueError("The provider credential must be printable ASCII without spaces.")
        seconds = self.timeout_seconds
        if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("The provider timeout must be a finite, positive number of seconds.")
        if type(self.max_response_bytes) is not int or self.max_response_bytes <= 0:
            raise ValueError("The provider response limit must be a positive number of bytes.")

    @property
    def url(self) -> str:
        """The only URL this endpoint contacts."""
        return self.base_url.rstrip("/") + "/chat/completions"


def _check_origin(provider: str, base_url: str) -> None:
    url = urlsplit(base_url)
    official = base_url.rstrip("/") == REVIEWED_ORIGINS.get(provider)
    local = url.scheme == "http" and url.hostname in LOOPBACK_HOSTS
    extras = url.username or url.password or url.query or url.fragment
    if provider not in REVIEWED_ORIGINS or not (official or local) or extras:
        raise ValueError("The provider endpoint must be its reviewed origin or a loopback URL.")
    if local and (url.port in (None, 0) or url.path.rstrip("/") != "/v1"):
        raise ValueError("A loopback provider endpoint needs an explicit port and the path /v1.")
