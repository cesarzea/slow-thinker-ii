"""Server configurations derived from the step 1 example, written to temporary files."""

import copy
import json
import sys
from pathlib import Path
from types import MappingProxyType

from slow_thinker_ii.catalog import ComponentDeclaration, ComponentRef, parse_declaration
from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    decode_json,
    json_object,
    value_at_pointer,
)
from support.examples import EXAMPLES, ROOT, changed, server_configuration

EXAMPLE = ROOT / "examples/server-configuration.json"
TOKEN = "bootstrap-tests-operator-token-0123456789"
SECRETS = MappingProxyType(
    {"OPENAI_API_KEY": "sk-openai-test-key", "DEEPSEEK_API_KEY": "sk-deepseek-test-key"}
)
ENVIRONMENT = MappingProxyType({"SLOW_THINKER_OPERATOR_TOKEN": TOKEN, **SECRETS})
MODULES = MappingProxyType({"llm-call": "slow_thinker_llm_call", "router": "slow_thinker_router"})


def local(directory: Path, public_url: str = "http://127.0.0.1:8000") -> JsonObject:
    """The example with its state under `directory`, no interface and no installed resolutions."""
    document = changed(server_configuration(), ("database",), str(directory / "state.sqlite3"))
    document = changed(document, ("workspace",), str(directory / "runs"))
    document = changed(document, ("server", "static_directory"), None)
    document = changed(document, ("server", "public_url"), public_url)
    host = public_url.split("://", 1)[1]
    document = changed(document, ("server", "allowed_hosts"), [host])
    return changed(document, ("components", "resolutions"), [])


def simulated(document: JsonObject, replies: dict[str, list[str]] | None = None) -> JsonObject:
    """Every model answered by the simulated provider, which needs no credential."""
    result = changed(document, ("llm", "providers"), {"simulated": {}})
    llm = json_object(result["llm"])
    models = llm["models"]
    assert isinstance(models, list)
    for model in models:
        assert isinstance(model, dict)
        model["provider"] = "simulated"
        scripted = (replies or {}).get(str(model["id"]))
        if scripted is not None:
            model["replies"] = list[JsonValue](scripted)
    return changed(result, ("llm",), llm)


def without(document: JsonObject, path: tuple[str | int, ...]) -> JsonObject:
    """A deep copy of `document` without the object member at `path`."""
    result = copy.deepcopy(document)
    parent = value_at_pointer(result, path[:-1])
    assert isinstance(parent, dict)
    del parent[str(path[-1])]
    return result


def written(directory: Path, document: JsonValue, name: str = "configuration.json") -> Path:
    path = directory / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def package_declarations() -> tuple[ComponentDeclaration, ...]:
    """LLM Call and Router as the contract examples declare them."""
    names = ("llm-call", "router")
    return tuple(
        parse_declaration(decode_json((EXAMPLES / f"{name}.component.json").read_text()))
        for name in names
    )


class DevelopmentTargets:
    """Launch targets from the development environment's editable component packages."""

    def interpreter(self, ref: ComponentRef) -> Path:
        return Path(sys.executable)

    def module(self, ref: ComponentRef) -> str:
        return MODULES[ref.type]
