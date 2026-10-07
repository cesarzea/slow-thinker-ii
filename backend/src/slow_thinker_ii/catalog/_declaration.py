"""Validated component declarations and the output ports they expose."""

import re
from dataclasses import dataclass

from slow_thinker_ii.contracts import JsonObject, parse_pointer, value_at_pointer

from ._refs import ComponentRef

PORT_NAME = re.compile(r"[a-z][a-z0-9_]{0,31}")


@dataclass(frozen=True)
class ServiceUse:
    service: str
    pointer: str


@dataclass(frozen=True)
class ComponentDeclaration:
    ref: ComponentRef
    label: str
    placements: frozenset[str]
    stateful: bool
    inputs: tuple[str, ...]
    outputs: tuple[str, ...] | None
    outputs_from: str | None
    uses: tuple[ServiceUse, ...]
    config_schema: JsonObject
    initial_config: JsonObject
    document: JsonObject

    def output_ports(self, config: JsonObject) -> tuple[str, ...]:
        """Declared outputs, or the distinct valid port names configured at `outputs_from`."""
        if self.outputs is not None:
            return self.outputs
        if self.outputs_from is None:
            return ()
        configured = value_at_pointer(config, parse_pointer(self.outputs_from))
        names = configured if isinstance(configured, list) else []
        valid = [name for name in names if isinstance(name, str) and PORT_NAME.fullmatch(name)]
        return tuple(sorted(set(valid), key=valid.index))
