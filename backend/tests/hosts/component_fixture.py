"""A host program for adapter tests, built on the host SDK; never an installed component.

Run as `component_fixture.py <bootstrap> <launch arguments as JSON>`. The configuration's
`mode` sets the startup and shutdown behaviour, each received message the call's.
"""

import asyncio
import json
import os
import signal
import sys
import time
from collections.abc import Sequence
from pathlib import Path

from slow_thinker_host import (
    Bootstrap,
    Context,
    Emission,
    HandlerError,
    JsonValue,
    read_bootstrap,
    run_host,
)


class Fixture:
    def __init__(self, bootstrap: Bootstrap, arguments: JsonValue) -> None:
        outputs = bootstrap.config.get("outputs")
        self._port = outputs[0] if isinstance(outputs, list) and outputs else "out"
        self._facts: JsonValue = {
            "arguments": arguments,
            "environment": {key: value for key, value in os.environ.items()},
            "directory": os.getcwd(),
            "session_leader": os.getsid(0) == os.getpid(),
        }

    async def activate(self, message: JsonValue, context: Context) -> Sequence[Emission]:
        return [Emission(str(self._port), await self._answer(message, context))]

    async def select_output(
        self, received: JsonValue, node_input: JsonValue, context: Context
    ) -> Emission:
        answer = await self._answer(received, context)
        return Emission(str(self._port), {"received": answer, "node_input": node_input})

    async def _answer(self, message: JsonValue, context: Context) -> JsonValue:
        request = message if isinstance(message, dict) else {}
        if request.get("wait"):
            try:
                await asyncio.Event().wait()
            finally:
                Path(f"cancelled-{context.activation_id}").touch()
        if isinstance(fail := request.get("fail"), list):
            raise HandlerError(str(fail[0]), str(fail[1]))
        if isinstance(delay := request.get("sleep"), int | float):
            await asyncio.sleep(delay)
        if isinstance(size := request.get("big"), int):
            return "x" * size
        if request.get("crash"):
            os._exit(5)
        return self._facts if request.get("facts") else message


def start(bootstrap: Bootstrap, mode: str) -> None:
    Path(f"{bootstrap.node_id}.{bootstrap.position}.pid").write_text(str(os.getpid()))
    Path(f"{bootstrap.node_id}.{bootstrap.position}.started").write_text(repr(time.time()))
    if mode == "exit":
        sys.stderr.write("Starting the fixture.\nFixture startup failed: told to exit.\n")
        raise SystemExit(3)
    if mode in ("hang", "malformed"):
        if mode == "malformed":
            sys.stdout.write("this is not JSON-RPC\n")
            sys.stdout.flush()
        time.sleep(60)
        raise SystemExit(0)
    if mode == "slow":
        time.sleep(0.5)
    if mode == "stubborn":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)


def main() -> None:
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    mode = str(bootstrap.config.get("mode", "serve"))
    start(bootstrap, mode)
    fixture = Fixture(bootstrap, json.loads(sys.argv[2]))
    run_host(bootstrap, node=fixture, output=fixture)
    if mode in ("stubborn", "linger"):
        time.sleep(60)


if __name__ == "__main__":
    main()
