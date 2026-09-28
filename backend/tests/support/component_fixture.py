"""Controlled process failures for transport integration tests; never a registered component."""

import asyncio
import signal
import sys
import time
from pathlib import Path

from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, JsonObject, Operation, ToolReply, run_stdio

SCHEMA: JsonObject = {"type": "object"}


class Fixture:
    def operations(self) -> tuple[Operation, ...]:
        return (Operation("wait", SCHEMA, SCHEMA),)

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del name, context
        Path("invoked").touch()
        if arguments.get("error"):
            raise MCPError(code=-32001, message="fixture failure", data={"origin": "fixture"})
        if arguments.get("wait"):
            try:
                await asyncio.Event().wait()
            finally:
                Path("cancelled").touch()
        return ToolReply({"done": True})


def main() -> None:
    mode = Path(sys.argv[-1]).read_text()
    if mode == "stubborn":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        Path("started").touch()
        time.sleep(60)
    elif mode == "malformed":
        sys.stdout.write("invalid protocol frame\n")
        sys.stdout.flush()
        time.sleep(60)
    else:
        run_stdio(Fixture(), "transport-fixture", "1")


if __name__ == "__main__":
    main()
