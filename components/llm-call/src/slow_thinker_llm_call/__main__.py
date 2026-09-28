"""Installed LLMCall host; bootstrap configuration contains no provider credentials."""

import sys
from pathlib import Path

from slow_thinker_host import json_object, read_bootstrap, run_stdio

from ._config import parse_config
from ._endpoint import endpoint_from_record
from ._hosting import LLMCallHost


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if len(bootstrap.operations) != 1 or set(bootstrap.clients) != {"openai"}:
        raise ValueError("LLMCall requires one operation and its managed OpenAI binding")
    endpoint = endpoint_from_record(json_object(bootstrap.clients["openai"]))
    host = LLMCallHost(
        parse_config(bootstrap.config), bootstrap.operations[0], endpoint.client, endpoint.model
    )
    run_stdio(host, "llm-call", "0.1.0.dev1")


if __name__ == "__main__":
    main()
