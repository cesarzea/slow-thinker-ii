"""The server section: its public origin, operator access and the compiled interface."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from ._document import ServerDocument, invalid

LOOPBACK_HOST = re.compile(r"(?:127\.0\.0\.1|localhost|\[::1\])(?::[0-9]{1,5})?")


@dataclass(frozen=True)
class ServerSection:
    public_url: str  # scheme://host[:port], which component hosts call back
    allowed_hosts: tuple[str, ...]
    allowed_origins: tuple[str, ...]
    static_directory: Path | None
    operator_authentication: Literal["token", "none"]  # "none": loopback hosts only


def server_section(document: ServerDocument) -> ServerSection:
    """The checked section; `"none"` is refused unless every allowed host is a loopback one."""
    url = urlsplit(document.public_url)
    origin = f"{url.scheme}://{url.netloc}"
    exact = document.public_url.rstrip("/") == origin and "@" not in url.netloc
    if url.scheme not in ("http", "https") or not url.hostname or not exact:
        raise invalid("/server/public_url", "it must be an origin such as http://127.0.0.1:8000")
    hosts, access = document.allowed_hosts, document.operator_authentication
    if access == "none" and not all(LOOPBACK_HOST.fullmatch(host) for host in hosts):
        raise invalid(
            "/server/operator_authentication",
            '"none" requires every allowed host to be a loopback address',
        )
    static = document.static_directory
    directory = None if static is None else Path(static).absolute()
    return ServerSection(origin, hosts, document.allowed_origins, directory, access)
