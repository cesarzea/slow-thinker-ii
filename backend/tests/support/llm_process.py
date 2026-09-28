"""Loopback-only model endpoint and trusted bootstrap for real subprocess tests."""

import asyncio
import sys
from pathlib import Path

from slow_thinker_host import JsonObject, decode_json, encode_json, json_object
from slow_thinker_ii.adapters.process import ComponentProcess, ProcessLaunch
from slow_thinker_ii.contracts import OperationContract
from slow_thinker_llm_call import effective_operation

from .openai_calls import bootstrap_record, completion, config


class ModelEndpoint:
    def __init__(self) -> None:
        self.requests: list[JsonObject] = []
        self.authority: list[bytes] = []

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            header = await reader.readuntil(b"\r\n\r\n")
            lines = header.split(b"\r\n")
            assert lines[0] == b"POST /v1/chat/completions HTTP/1.1"
            fields = dict(line.lower().split(b": ", 1) for line in lines[1:] if b": " in line)
            raw = await reader.readexactly(int(fields[b"content-length"]))
            self.requests.append(json_object(decode_json(raw.decode())))
            self.authority.append(fields[b"authorization"])
            response = encode_json(completion("success")).encode()
            writer.write(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n"
                + f"Content-Length: {len(response)}\r\n\r\n".encode()
                + response
            )
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()


def llm_process(directory: Path, port: int) -> ComponentProcess:
    settings = config()
    operation = effective_operation(settings)
    bootstrap = directory / "llm.json"
    bootstrap.write_text(encode_json(bootstrap_record(f"http://127.0.0.1:{port}/v1/")))
    contract = OperationContract(
        operation.name, encode_json(operation.input_schema), encode_json(operation.output_schema)
    )
    launch = ProcessLaunch(
        Path(sys.executable), "slow_thinker_llm_call", bootstrap, directory, 5, 3, 1_048_576
    )
    return ComponentProcess(launch, (contract,))
