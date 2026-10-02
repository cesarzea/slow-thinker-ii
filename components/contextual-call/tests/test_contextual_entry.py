"""The installed composition requires one declared operation and trusted MCP bindings."""

from pathlib import Path

import pytest
from context_case import CONFIG
from slow_thinker_contextual_call import ContextualCallHost
from slow_thinker_host import JsonObject

from tooling.tests.test_external_entry_support import invalid_argv, invoke_entry

CLIENTS: JsonObject = {
    "mcp": {
        "url": "http://127.0.0.1:8000/mcp",
        "timeout_seconds": 3,
        "close_seconds": 1,
        "resources": {
            "worker": {"work": "work"},
            "memory": {"get": "get", "put": "put"},
            "calculator": {"calculate": "calculate"},
        },
    }
}


def test_contextual_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    invalid_argv("slow_thinker_contextual_call", monkeypatch)
    assert invoke_entry(
        "slow_thinker_contextual_call",
        CONFIG,
        ContextualCallHost.describe(CONFIG),
        CLIENTS,
        tmp_path,
        monkeypatch,
    ) == ["contextual-call"]
    with pytest.raises(ValueError):
        invoke_entry("slow_thinker_contextual_call", CONFIG, (), {}, tmp_path, monkeypatch)
