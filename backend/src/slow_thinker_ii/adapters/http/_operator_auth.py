"""The operator token is separate from invocation grants and provider credentials."""

from ipaddress import ip_address
from secrets import compare_digest

from starlette.datastructures import Headers
from starlette.types import Scope

from ._operator_errors import ACCESS, PREFIX, OperatorError
from ._settings import HttpSettings


class OperatorAccess:
    """Checks, in order: one exact allowed host, a browser origin when present, then the token.

    Without a configured token there is no operator authentication, and the peer must be this
    machine instead. `GET /api/v2/access` never needs the token.
    """

    def __init__(self, settings: HttpSettings) -> None:
        token = settings.operator_token
        self._expected = None if token is None else f"Bearer {token}".encode()
        self._hosts = settings.allowed_hosts
        self._origins = settings.allowed_origins

    @property
    def authentication(self) -> str:
        """`token` when operator requests need the token, otherwise `none`."""
        return "none" if self._expected is None else "token"

    def denial(self, scope: Scope) -> OperatorError | None:
        """The refusal of an operator request, or `None` when it may proceed."""
        headers = Headers(scope=scope)
        refusal = self._place_denial(headers)
        if refusal is not None:
            return refusal
        if self._expected is None:
            return None if _loopback(scope) else _client_denied()
        if _public(scope):
            return None
        return _token_denial(headers.getlist("authorization"), self._expected)

    def _place_denial(self, headers: Headers) -> OperatorError | None:
        if headers.getlist("host") not in ([host] for host in self._hosts):
            message = "This server does not answer operator requests for that host."
            return OperatorError(403, "operator_host_denied", message)
        origins = headers.getlist("origin")
        cross_site = headers.get("sec-fetch-site") == "cross-site"
        if cross_site or (origins and origins not in ([origin] for origin in self._origins)):
            message = "Operator requests from this origin are not allowed."
            return OperatorError(403, "operator_origin_denied", message)
        return None


def _public(scope: Scope) -> bool:
    """Only `GET /api/v2/access` is answered without the operator token."""
    return scope["method"] == "GET" and scope["path"] == f"{PREFIX}{ACCESS}"


def _loopback(scope: Scope) -> bool:
    """Whether the peer is in 127.0.0.0/8 or is ::1 (IPv4-mapped forms included).

    A connection without a client address is not this machine."""
    client = scope.get("client")
    try:
        return ip_address(str(client[0]) if client else "").is_loopback
    except ValueError:
        return False


def _client_denied() -> OperatorError:
    message = "Requests without an operator token are accepted only from this machine."
    return OperatorError(403, "operator_client_denied", message)


def _token_denial(credentials: list[str], expected: bytes) -> OperatorError | None:
    if len(credentials) == 1 and compare_digest(credentials[0].encode(), expected):
        return None
    message = "Send the operator token as a bearer credential."
    return OperatorError(401, "operator_authentication_required", message)
