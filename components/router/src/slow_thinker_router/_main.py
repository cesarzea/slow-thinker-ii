"""Start a Router host from the bootstrap document named on the command line."""

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn, Protocol

from slow_thinker_host import (
    Bootstrap,
    NodeHandler,
    OutputHandler,
    check_bootstrap,
    read_bootstrap,
    read_declaration,
    run_host,
)

from ._config import parse_config
from ._router import Router
from ._script import load_route


class Serve(Protocol):
    def __call__(
        self, bootstrap: Bootstrap, *, node: NodeHandler, output: OutputHandler
    ) -> None: ...


def main(arguments: Sequence[str], serve: Serve = run_host) -> None:
    """Load the script before serving; a startup failure prints why and exits with 1."""
    if len(arguments) != 1:
        _fail("expected exactly one argument, the bootstrap document path")
    try:
        bootstrap = read_bootstrap(Path(arguments[0]))
        check_bootstrap(bootstrap, read_declaration("slow_thinker_router"))
        settings = parse_config(bootstrap.config)
        router = Router(settings, load_route(settings.script))
    except (OSError, ValueError) as error:
        _fail(str(error))
    serve(bootstrap, node=router, output=router)


def _fail(reason: str) -> NoReturn:
    sys.stderr.write(f"Router startup failed: {reason}\n")
    raise SystemExit(1)
