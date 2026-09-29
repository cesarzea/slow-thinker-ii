"""Launch the inherited reviewer with the same managed client boundary as LLMCall."""

import sys
from pathlib import Path

from slow_thinker_host import json_object, read_bootstrap, run_stdio
from slow_thinker_llm_call import LLMCallHost, endpoint_from_record, parse_config

from ._review import GroundedReview


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if (
        len(bootstrap.operations) != 1
        or "openai" not in bootstrap.clients
        or set(bootstrap.clients) - {"openai", "mcp"}
    ):
        raise ValueError("GroundedReview requires one operation and its managed OpenAI binding")
    endpoint = endpoint_from_record(json_object(bootstrap.clients["openai"]))
    host = LLMCallHost(
        parse_config(bootstrap.config),
        bootstrap.operations[0],
        endpoint.client,
        endpoint.model,
        implementation=GroundedReview,
    )
    run_stdio(host, "grounded-review", "0.1.0.dev1")


if __name__ == "__main__":
    main()
