"""Reuse the public managed-model host; no provider secret enters this agent."""

import sys
from pathlib import Path

from slow_thinker_host import json_object, read_bootstrap, run_stdio
from slow_thinker_llm_call import LLMCallHost, endpoint_from_record, parse_config

from . import ResourceAgent


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if len(bootstrap.operations) != 1 or "openai" not in bootstrap.clients:
        raise ValueError("ResourceAgent requires one operation and its managed model binding")
    if set(bootstrap.clients) - {"openai", "mcp"}:
        raise ValueError("Unsupported ResourceAgent client binding")
    endpoint = endpoint_from_record(json_object(bootstrap.clients["openai"]))
    host = LLMCallHost(
        parse_config(bootstrap.config),
        bootstrap.operations[0],
        endpoint.client,
        endpoint.model,
        implementation=ResourceAgent,
    )
    run_stdio(host, "resource-agent", "0.1.0")


if __name__ == "__main__":
    main()
