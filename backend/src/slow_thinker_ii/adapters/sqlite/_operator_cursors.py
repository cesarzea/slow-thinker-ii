"""Authenticated cursors freeze the row boundary and bind paging to one query."""

from base64 import urlsafe_b64decode, urlsafe_b64encode
from hashlib import sha256
from hmac import compare_digest, new

from slow_thinker_ii.application import InvalidCursor
from slow_thinker_ii.contracts import decode_json, encode_json, json_object


class OperatorCursors:
    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("Paging cursors need an explicit random signing key")
        self._key = key

    def encode(self, scope: str, through: int, after: int) -> str:
        body = encode_json({"scope": scope, "through": through, "after": after}).encode()
        return urlsafe_b64encode(body).decode() + "." + new(self._key, body, sha256).hexdigest()

    def decode(self, token: str, scope: str) -> tuple[int, int]:
        try:
            if len(token) > 1024:
                raise ValueError("Oversized cursor")
            encoded, signature = token.split(".")
            body = urlsafe_b64decode(encoded)
            if not compare_digest(
                new(self._key, body, sha256).hexdigest().encode(), signature.encode()
            ):
                raise ValueError("Invalid cursor signature")
            value = json_object(decode_json(body.decode()))
            through, after = value["through"], value["after"]
            if (
                set(value) != {"scope", "through", "after"}
                or value["scope"] != scope
                or type(through) is not int
                or type(after) is not int
                or not 0 <= after <= through <= 2**63 - 1
            ):
                raise ValueError("Invalid cursor fields")
            return through, after
        except (ValueError, KeyError, UnicodeError) as error:
            raise InvalidCursor("Invalid or foreign paging cursor") from error
