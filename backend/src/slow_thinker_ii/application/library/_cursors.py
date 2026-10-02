"""Signed process-local positions for one immutable library listing window."""

from base64 import b64decode, urlsafe_b64encode
from dataclasses import dataclass
from hashlib import sha256
from hmac import compare_digest, new

from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from ._records import DefinitionError


@dataclass(frozen=True)
class Position:
    bundle: int = 0
    after: int = 0
    through: int | None = None


class LibraryCursors:
    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("Library cursors require a signing key of at least 32 bytes")
        self._key = key

    def encode(self, position: Position, limit: int) -> str:
        body = encode_json(
            {
                "scope": "definitions-v1",
                "limit": limit,
                "bundle": position.bundle,
                "after": position.after,
                "through": position.through,
            }
        ).encode("utf-8")
        return (
            urlsafe_b64encode(body).decode("ascii") + "." + new(self._key, body, sha256).hexdigest()
        )

    def decode(self, token: str, limit: int, bundles: int) -> Position:
        try:
            if len(token) > 1024:
                raise ValueError("Invalid cursor size")
            encoded, signature = token.split(".")
            body = b64decode(encoded, altchars=b"-_", validate=True)
            expected = new(self._key, body, sha256).hexdigest().encode("ascii")
            if not compare_digest(expected, signature.encode("ascii")):
                raise ValueError("Invalid cursor signature")
            return position(json_object(decode_json(body.decode("utf-8"))), limit, bundles)
        except (ValueError, KeyError, UnicodeError, RecursionError) as error:
            raise DefinitionError("invalid_cursor") from error


def position(value: JsonObject, limit: int, bundles: int) -> Position:
    if set(value) != {"scope", "limit", "bundle", "after", "through"}:
        raise ValueError("Invalid cursor fields")
    if value["scope"] != "definitions-v1" or type(value["limit"]) is not int:
        raise ValueError("Invalid cursor binding")
    if value["limit"] != limit:
        raise ValueError("Invalid cursor page size")
    bundle, after, through = value["bundle"], value["after"], value["through"]
    if type(bundle) is not int or type(after) is not int or type(through) is not int:
        raise ValueError("Invalid cursor position")
    if not 0 <= bundle <= bundles or not 0 <= after <= through <= 2**63 - 1:
        raise ValueError("Invalid cursor range")
    if bundle < bundles and after != 0:
        raise ValueError("Invalid cursor ordering")
    return Position(bundle, after, through)
