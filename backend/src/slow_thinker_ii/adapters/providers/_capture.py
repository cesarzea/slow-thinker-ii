"""Bounded reading of provider responses and credential redaction of everything returned."""

import httpx

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json

REDACTED = "[redacted]"
CHUNK_BYTES = 16_384


class CaptureLimit(Exception):
    """The response body exceeds the endpoint's `max_response_bytes`."""


async def read_body(response: httpx.Response, limit: int) -> bytes:
    """The decoded body, read until `limit` bytes; one byte more raises `CaptureLimit`."""
    chunks: list[bytes] = []
    size = 0
    async for chunk in response.aiter_bytes(chunk_size=min(limit + 1, CHUNK_BYTES)):
        size += len(chunk)
        if size > limit:
            raise CaptureLimit
        chunks.append(chunk)
    return b"".join(chunks)


def decoded(raw: bytes) -> JsonValue:
    """The JSON value of a UTF-8 body; `None` when the body is not JSON."""
    try:
        return decode_json(raw.decode("utf-8"))
    except (ValueError, RecursionError):
        return None


def redacted_text(text: str, secret: str) -> str:
    return text.replace(secret, REDACTED)


def redacted_object(value: JsonObject, secret: str) -> JsonObject:
    """`value` with every occurrence of `secret` in its keys and strings replaced."""
    return {redacted_text(key, secret): _redacted(item, secret) for key, item in value.items()}


def _redacted(value: JsonValue, secret: str) -> JsonValue:
    if isinstance(value, str):
        return redacted_text(value, secret)
    if isinstance(value, list):
        return [_redacted(item, secret) for item in value]
    if isinstance(value, dict):
        return redacted_object(value, secret)
    return value
