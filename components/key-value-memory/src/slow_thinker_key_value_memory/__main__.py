"""Bootstrap accepts only a trusted memory path and effective namespace."""

import sys
from pathlib import Path

from slow_thinker_host import json_object, read_bootstrap, run_stdio

from . import KeyValueMemoryHost


def main() -> None:
    if len(sys.argv) != 2:
        raise ValueError("Expected one trusted bootstrap path")
    bootstrap = read_bootstrap(Path(sys.argv[1]))
    if set(bootstrap.clients) != {"memory_store"}:
        raise ValueError("Memory requires its trusted store binding")
    store = json_object(bootstrap.clients["memory_store"])
    path, namespace = store.get("path"), store.get("namespace")
    if (
        set(store) != {"path", "namespace"}
        or not isinstance(path, str)
        or not isinstance(namespace, str)
    ):
        raise ValueError("Invalid trusted memory store binding")
    if not Path(path).is_absolute() or not namespace:
        raise ValueError("Memory requires an absolute trusted path and nonempty namespace")
    host = KeyValueMemoryHost(bootstrap.config, bootstrap.operations, Path(path), namespace)
    run_stdio(host, "key-value-memory", "0.1.0")


if __name__ == "__main__":
    main()
