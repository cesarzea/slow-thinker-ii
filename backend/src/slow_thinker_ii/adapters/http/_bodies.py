"""Request bodies are read in bounded chunks, never beyond the configured limit."""

import re

from fastapi import Request

JSON_MEDIA_TYPE = "application/json"
_LENGTH = re.compile(r"[0-9]+")


def media_type(request: Request) -> str:
    """The declared media type without parameters, in lower case; empty when absent."""
    return request.headers.get("content-type", "").split(";", 1)[0].strip().lower()


async def bounded_body(request: Request, limit: int) -> bytes | None:
    """The complete body, or `None` as soon as it is known to exceed `limit` bytes."""
    if _declares_more(request.headers.get("content-length", ""), limit):
        return None
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            return None
        chunks.append(chunk)
    return b"".join(chunks)


def _declares_more(declared: str, limit: int) -> bool:
    """Whether a `Content-Length` value announces more than `limit` bytes."""
    if _LENGTH.fullmatch(declared) is None:
        return False
    digits = declared.lstrip("0") or "0"
    return len(digits) > 18 or int(digits) > limit
