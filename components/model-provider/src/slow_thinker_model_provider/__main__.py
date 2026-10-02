"""Start the resource with an explicitly supplied provider credential and immutable bootstrap."""

import os
import sys
from pathlib import Path

from slow_thinker_host import json_object, read_bootstrap, run_stdio

from ._config import parse_config
from ._endpoint import endpoint_from_record
from ._hosting import ModelProviderHost
from ._transport import ProviderTransport


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    credential = os.environ.pop("SLOW_THINKER_SECRET_MODEL", "")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if (
        len(bootstrap.operations) != 1
        or "provider" not in bootstrap.clients
        or set(bootstrap.clients) - {"provider", "mcp"}
    ):
        raise ValueError("The model resource requires one operation and provider binding")
    config = parse_config(bootstrap.config)
    endpoint = endpoint_from_record(
        json_object(bootstrap.clients["provider"]), credential, config.provider
    )
    run_stdio(
        ModelProviderHost(config, bootstrap.operations[0], ProviderTransport(endpoint)),
        "model-provider",
        "0.1.0",
    )


if __name__ == "__main__":
    main()
