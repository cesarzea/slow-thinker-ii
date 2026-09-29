"""Installed bounded controller; stdout belongs exclusively to MCP."""

import sys
from pathlib import Path

from slow_thinker_host import read_bootstrap, run_stdio

from . import BoundedFlowHost


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if len(bootstrap.operations) != 1:
        raise ValueError("BoundedFlow exposes one operation")
    run_stdio(BoundedFlowHost(bootstrap.config, bootstrap.operations[0]), "bounded-flow", "0.1.0")


if __name__ == "__main__":
    main()
