"""Operator credentials are separate from component invocation grants and provider secrets."""

import re
from secrets import compare_digest
from urllib.parse import urlsplit

from fastapi import Request

from ._operator_errors import OperatorError


class OperatorAccess:
    def __init__(self, credential: str, origins: tuple[str, ...], hosts: tuple[str, ...]) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_-]{32,128}", credential):
            raise ValueError(
                "Use a randomly generated operator credential of at least 32 characters"
            )
        if not origins or not hosts:
            raise ValueError("Explicit operator origins and hosts are required")
        for origin in origins:
            value = urlsplit(origin)
            if value.scheme != "http" or value.hostname not in ("127.0.0.1", "localhost", "::1"):
                raise ValueError("The initial operator interface requires local HTTP origins")
            if value.username or value.password or value.path or value.query or value.fragment:
                raise ValueError("An operator origin must contain only scheme and authority")
            if value.netloc not in hosts:
                raise ValueError("Each origin requires an approved exact host")
        self._credential, self._origins, self._hosts = credential, origins, hosts

    def require(self, request: Request) -> None:
        if request.headers.getlist("host") not in ([host] for host in self._hosts):
            raise OperatorError("operator_host_denied", 403)
        origins = request.headers.getlist("origin")
        if origins and origins not in ([origin] for origin in self._origins):
            raise OperatorError("operator_origin_denied", 403)
        if request.headers.get("sec-fetch-site") == "cross-site":
            raise OperatorError("operator_origin_denied", 403)
        credentials = request.headers.getlist("authorization")
        expected = "Bearer " + self._credential
        if len(credentials) != 1 or not compare_digest(credentials[0].encode(), expected.encode()):
            raise OperatorError("operator_authentication_required", 401)
