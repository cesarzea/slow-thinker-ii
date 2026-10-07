"""Start an LLM Call host from the bootstrap document named on the command line."""

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn, Protocol

from slow_thinker_host import (
    Bootstrap,
    NodeHandler,
    check_bootstrap,
    read_bootstrap,
    read_declaration,
    run_host,
)

from ._component import LLMCall
from ._config import parse_config


class Serve(Protocol):
    def __call__(self, bootstrap: Bootstrap, *, node: NodeHandler) -> None: ...


def main(arguments: Sequence[str], serve: Serve = run_host) -> None:
    """Check the bootstrap and configuration, then serve; startup failures exit with 1."""
    if len(arguments) != 1:
        _fail("expected exactly one argument, the bootstrap document path")
    try:
        bootstrap = read_bootstrap(Path(arguments[0]))
        check_bootstrap(bootstrap, read_declaration("slow_thinker_llm_call"))
        node = LLMCall(parse_config(bootstrap.config))
    except (OSError, ValueError) as error:
        _fail(str(error))
    serve(bootstrap, node=node)


def _fail(reason: str) -> NoReturn:
    sys.stderr.write(f"LLM Call startup failed: {reason}\n")
    raise SystemExit(1)
