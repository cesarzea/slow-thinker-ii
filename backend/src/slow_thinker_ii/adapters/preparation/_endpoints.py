"""Native transports are selected by the backend, not by graph-authored configuration."""

from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class ServiceEndpoints:
    gateway: str
    provider: str = "https://api.openai.com/v1"

    def __post_init__(self) -> None:
        require_loopback(self.gateway)
        if self.provider != "https://api.openai.com/v1":
            require_loopback(self.provider)


def require_loopback(url: str) -> None:
    value = urlsplit(url)
    if (
        value.scheme != "http"
        or value.hostname not in ("127.0.0.1", "::1")
        or value.port is None
        or value.port < 1
        or value.path != "/v1"
        or value.username is not None
        or value.password is not None
        or value.query
        or value.fragment
    ):
        raise ValueError("A native local endpoint must use an explicit loopback /v1 address")
