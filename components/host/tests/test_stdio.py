"""`run_host` serves newline-delimited MCP on standard I/O and returns when stdin closes."""

import io
import os
import select
import sys
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager

import pytest
from host_fixtures import Recorder, bootstrap, meta
from slow_thinker_host import (
    PROTOCOL_VERSION,
    JsonObject,
    JsonValue,
    decode_json,
    encode_json,
    json_object,
    run_host,
)

ENVELOPE: JsonObject = {
    "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
    "io.modelcontextprotocol/clientInfo": {"name": "platform", "version": "1"},
    "io.modelcontextprotocol/clientCapabilities": {},
}


def request(identifier: int, method: str, params: JsonObject) -> bytes:
    line: JsonObject = {"jsonrpc": "2.0", "id": identifier, "method": method, "params": params}
    return (encode_json(line) + "\n").encode()


def call(message: JsonValue) -> JsonObject:
    return {
        "_meta": {**ENVELOPE, **meta()},
        "name": "activate",
        "arguments": {"message": message},
    }


def member(value: JsonValue, key: str) -> JsonValue:
    assert isinstance(value, dict)
    return value[key]


@contextmanager
def piped_stdio(monkeypatch: pytest.MonkeyPatch) -> Generator[tuple[io.BufferedWriter, int]]:
    """Replace stdin and stdout with pipes; yield the request writer and response reader."""
    in_read, in_write = os.pipe()
    out_read, out_write = os.pipe()
    with (
        open(in_read, "rb") as stdin_bytes,
        open(out_write, "wb") as stdout_bytes,
        open(in_write, "wb") as writer,
    ):
        stdin = io.TextIOWrapper(stdin_bytes, encoding="utf-8")
        stdout = io.TextIOWrapper(stdout_bytes, encoding="utf-8")
        monkeypatch.setattr(sys, "stdin", stdin)
        monkeypatch.setattr(sys, "stdout", stdout)
        try:
            yield writer, out_read
        finally:
            stdin.close()
            stdout.close()
            os.close(out_read)


def response(descriptor: int) -> JsonObject:
    line = b""
    while not line.endswith(b"\n"):
        ready, _, _ = select.select([descriptor], [], [], 5)
        assert ready, "The host did not answer"
        line += os.read(descriptor, 1)
    return json_object(decode_json(line.decode()))


def test_run_host_answers_until_stdin_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    with piped_stdio(monkeypatch) as (requests, responses):
        serving = threading.Thread(
            target=run_host, args=(bootstrap(),), kwargs={"node": Recorder()}
        )
        serving.start()
        requests.write(request(1, "tools/list", {"_meta": ENVELOPE}))
        requests.flush()
        listed = response(responses)
        requests.write(request(2, "tools/call", call("hi")))
        requests.flush()
        called = response(responses)
        requests.close()
        serving.join(timeout=5)
        assert not serving.is_alive()
    tools = member(member(listed, "result"), "tools")
    assert isinstance(tools, list) and [member(tool, "name") for tool in tools] == ["activate"]
    assert member(member(called, "result"), "structuredContent") == {
        "emissions": [{"port": "out", "payload": "hi"}]
    }


def test_closing_stdin_cancels_running_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    handler = Recorder()
    handler.release.clear()
    with piped_stdio(monkeypatch) as (requests, _):
        serving = threading.Thread(target=run_host, args=(bootstrap(),), kwargs={"node": handler})
        serving.start()
        requests.write(request(1, "tools/call", call(1)))
        requests.flush()
        for _ in range(500):
            if handler.running:
                break
            time.sleep(0.01)
        assert handler.running == 1
        requests.close()
        serving.join(timeout=5)
        assert not serving.is_alive()
    assert handler.running == 0


def test_run_host_requires_the_handler_of_its_position() -> None:
    with pytest.raises(ValueError, match="requires an output handler"):
        run_host(bootstrap("output"), node=Recorder())
