"""Run the installed calculator using only trusted host bootstrap."""

import sys
from pathlib import Path

from slow_thinker_host import read_bootstrap, run_stdio

from . import CalculatorHost


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if bootstrap.clients:
        raise ValueError("Calculator does not accept client bindings")
    run_stdio(CalculatorHost(bootstrap.config, bootstrap.operations), "calculator", "0.1.0")


if __name__ == "__main__":
    main()
