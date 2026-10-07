"""Failures are single attempts answered 502 or 504; credentials never leave the adapter."""

import httpx
import pytest
from slow_thinker_ii.contracts import JsonValue, encode_json
from support.examples import FLASH, LUNA

from .fixtures import SECRET, chat, completion, error_of, http_provider, model


def faulty(fault: str, request: httpx.Request) -> httpx.Response:
    """A failure whose exception text quotes the credential, as a careless transport might."""
    if fault == "timeout":
        raise httpx.ReadTimeout(SECRET, request=request)
    if fault == "connection":
        raise httpx.ConnectError(SECRET, request=request)
    contents = {"body_size": b"x" * 100, "not_json": b"bad", "array": b"[]", "not_utf8": b"\xff"}
    return httpx.Response(200, content=contents[fault])


@pytest.mark.parametrize(
    ("fault", "status", "message"),
    [
        ("timeout", 504, "The provider did not answer within 30 seconds."),
        ("connection", 502, "The connection to the provider failed (ConnectError)."),
        ("body_size", 502, "The provider's response exceeds 80 bytes."),
        ("not_json", 502, "The provider's response is not a JSON object."),
        ("array", 502, "The provider's response is not a JSON object."),
        ("not_utf8", 502, "The provider's response is not a JSON object."),
    ],
)
async def test_uncertain_or_invalid_outcomes_are_never_retried(
    fault: str, status: int, message: str
) -> None:
    provider, exchanges = http_provider(lambda request: faulty(fault, request), limit=80)
    reply = await provider.complete(model(FLASH), chat(FLASH), 30)
    assert len(exchanges.requests) == 1 and SECRET not in str(reply)
    assert (reply.status, reply.usage, error_of(reply)["message"]) == (status, None, message)


async def test_a_body_at_the_limit_is_read() -> None:
    body = encode_json(completion()).encode()
    provider, _ = http_provider(lambda request: httpx.Response(200, content=body), limit=len(body))
    assert (await provider.complete(model(LUNA), chat(LUNA), 30)).body == completion()


@pytest.mark.parametrize(
    ("content", "detail"),
    [
        (b"", "no details."),
        (b"  <html>Bad gateway</html>\n", "<html>Bad gateway</html>"),
        (b'{"error": "plain"}', '{"error": "plain"}'),
        (b'{"error": {"message": " ", "code": "x"}}', '{"error": {"message": " ", "code": "x"}}'),
        (b'{"error": {"message": "Overloaded.", "code": null}}', "Overloaded."),
        (b'{"error": {"message": "Overloaded.", "code": ""}}', "Overloaded."),
        (b"x" * 600, "x" * 499 + "…"),
    ],
)
async def test_an_error_message_keeps_the_provider_detail(content: bytes, detail: str) -> None:
    provider, _ = http_provider(lambda request: httpx.Response(503, content=content))
    reply = await provider.complete(model(LUNA), chat(LUNA), 30)
    message = f"The provider answered with HTTP 503: {detail}"
    assert (reply.status, error_of(reply)["message"]) == (502, message)


async def test_a_reflected_credential_is_redacted_in_keys_and_values() -> None:
    reflected: JsonValue = {SECRET: {"nested": [f"Bearer {SECRET}", 1, True, None, 2.5]}}
    body = completion(echo=reflected)
    provider, _ = http_provider(lambda request: httpx.Response(200, json=body))
    reply = await provider.complete(model(LUNA), chat(LUNA), 30)
    assert reply.status == 200 and SECRET not in str(reply)
    assert reply.body["echo"] == {
        "[redacted]": {"nested": ["Bearer [redacted]", 1, True, None, 2.5]}
    }


@pytest.mark.parametrize(
    "content",
    [
        encode_json({"error": {"message": f"Invalid key {SECRET}.", "code": SECRET}}).encode(),
        f"Invalid key {SECRET}.".encode(),
    ],
)
async def test_a_reflected_credential_is_redacted_in_error_messages(content: bytes) -> None:
    provider, _ = http_provider(lambda request: httpx.Response(401, content=content))
    reply = await provider.complete(model(LUNA), chat(LUNA), 30)
    assert reply.status == 502 and SECRET not in str(reply)
    assert "Invalid key [redacted]." in str(error_of(reply)["message"])
