"""Trusted upstream identity; provider authentication never comes from a graph or invocation."""

import math
from dataclasses import dataclass, field
from urllib.parse import urlsplit

from slow_thinker_host import JsonObject


@dataclass(frozen=True)
class ProviderEndpoint:
    provider: str
    base_url: str
    api_key: str = field(repr=False)
    timeout_seconds: float = 60
    close_seconds: float = 2
    max_response_bytes: int = 524_288

    def __post_init__(self) -> None:
        url = urlsplit(self.base_url)
        approved = {"openai": "https://api.openai.com/v1", "deepseek": "https://api.deepseek.com"}
        official = self.base_url.rstrip("/") == approved.get(self.provider)
        local = url.scheme == "http" and url.hostname in {"127.0.0.1", "::1"}
        if (
            self.provider not in approved
            or not (official or local)
            or url.username
            or url.password
            or url.query
            or url.fragment
        ):
            raise ValueError("Unsupported upstream endpoint")
        if local and (url.port is None or url.port == 0 or url.path.rstrip("/") != "/v1"):
            raise ValueError("Invalid loopback test endpoint")
        if not self.api_key or any(not 33 <= ord(char) <= 126 for char in self.api_key):
            raise ValueError("Invalid provider credential")
        for seconds in (self.timeout_seconds, self.close_seconds):
            if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError("Provider timeouts must be finite and positive")
        if type(self.max_response_bytes) is not int or self.max_response_bytes <= 0:
            raise ValueError("Provider capture needs a positive byte bound")


def endpoint_from_record(record: JsonObject, credential: str, provider: str) -> ProviderEndpoint:
    if set(record) != {"base_url", "timeout_seconds", "close_seconds", "max_response_bytes"}:
        raise ValueError("Unsupported upstream configuration")
    url, timeout, close, limit = (
        record[key]
        for key in ("base_url", "timeout_seconds", "close_seconds", "max_response_bytes")
    )
    if not isinstance(url, str) or not isinstance(timeout, int | float):
        raise ValueError("Invalid upstream endpoint or timeout")
    if not isinstance(close, int | float) or type(limit) is not int:
        raise ValueError("Invalid upstream capture or cleanup limit")
    return ProviderEndpoint(provider, url, credential, timeout, close, limit)
