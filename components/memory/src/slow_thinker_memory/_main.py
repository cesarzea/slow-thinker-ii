"""Start a Memory host from the bootstrap document named on the command line."""

import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import NoReturn, Protocol

from slow_thinker_host import (
    Bootstrap,
    JsonValue,
    MemoryHandler,
    check_bootstrap,
    read_bootstrap,
    read_declaration,
    run_host,
)

from ._memory import Memory


class Serve(Protocol):
    def __call__(self, bootstrap: Bootstrap, *, memory: MemoryHandler, stateful: bool) -> None: ...


def _limit(config: Mapping[str, JsonValue]) -> int:
    value = config.get("max_exchanges")
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 100:
        raise ValueError("max_exchanges must be a whole number from 1 to 100")
    return value


def main(arguments: Sequence[str], serve: Serve = run_host) -> None:
    """Check the bootstrap and configuration, then serve; a startup failure exits with 1."""
    if len(arguments) != 1:
        _fail("expected exactly one argument, the bootstrap document path")
    try:
        bootstrap = read_bootstrap(Path(arguments[0]))
        check_bootstrap(bootstrap, read_declaration("slow_thinker_memory"))
        memory = Memory(_limit(bootstrap.config))
    except (OSError, ValueError) as error:
        _fail(str(error))
    serve(bootstrap, memory=memory, stateful=True)


def _fail(reason: str) -> NoReturn:
    sys.stderr.write(f"Memory startup failed: {reason}\n")
    raise SystemExit(1)
