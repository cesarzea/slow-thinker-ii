"""The Router configuration, checked against the packaged declaration at startup."""

from dataclasses import dataclass
from typing import cast

from slow_thinker_host import JsonObject, json_object, read_declaration, validate_value


@dataclass(frozen=True)
class RouterConfig:
    """The declared output names and the script that chooses among them."""

    outputs: tuple[str, ...]
    script: str


def parse_config(config: JsonObject) -> RouterConfig:
    """Raise ValueError unless `config` is valid against the Router's configuration schema."""
    declared = read_declaration("slow_thinker_router")["config_schema"]
    try:
        validate_value(config, json_object(declared))
    except ValueError as error:
        raise ValueError(f"The Router configuration is invalid: {error}") from error
    outputs = cast(list[str], config["outputs"])
    return RouterConfig(tuple(outputs), str(config["script"]))
