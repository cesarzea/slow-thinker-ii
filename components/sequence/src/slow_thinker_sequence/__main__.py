"""Installed sequence process; stdout is reserved for MCP."""

import sys
from pathlib import Path

from slow_thinker_host import read_bootstrap, run_stdio

from . import SequenceHost


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if len(bootstrap.operations) != 1:
        raise ValueError("The sequence controller exposes one operation")
    run_stdio(SequenceHost(bootstrap.config, bootstrap.operations[0]), "sequence", "0.1.0.dev1")


if __name__ == "__main__":
    main()
