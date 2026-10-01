"""Installed composition process with platform-supplied MCP bindings."""

import sys
from pathlib import Path

from slow_thinker_host import json_object, mcp_endpoint_from_record, read_bootstrap, run_stdio

from . import RoutedCallHost


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if len(bootstrap.operations) != 1 or set(bootstrap.clients) != {"mcp"}:
        raise ValueError("RoutedCall requires one operation and managed MCP bindings")
    endpoint = mcp_endpoint_from_record(json_object(bootstrap.clients["mcp"]))
    host = RoutedCallHost(bootstrap.config, bootstrap.operations[0], endpoint)
    run_stdio(host, "routed-call", "0.1.0")


if __name__ == "__main__":
    main()
