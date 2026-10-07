"""Component references: a component type and an exact version."""

import re
from dataclasses import dataclass

_REFERENCE = re.compile(
    r"[a-z][a-z0-9-]{0,63}@(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
)


@dataclass(frozen=True)
class ComponentRef:
    type: str
    version: str

    @staticmethod
    def parse(text: str) -> "ComponentRef":
        if _REFERENCE.fullmatch(text) is None:
            raise ValueError(f"Malformed component reference: {text!r}")
        component_type, version = text.split("@")
        return ComponentRef(component_type, version)

    def __str__(self) -> str:
        return f"{self.type}@{self.version}"


TRIGGER = ComponentRef("trigger", "1.0.0")
OUTPUT = ComponentRef("output", "1.0.0")
