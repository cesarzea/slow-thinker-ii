"""Explicit launch credentials are separate from recorded bootstrap configuration."""

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProcessSecret:
    name: str
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if not re.fullmatch(r"SLOW_THINKER_SECRET_[A-Z][A-Z0-9_]*", self.name):
            raise ValueError("Invalid managed secret name")
        if not self.value or "\x00" in self.value:
            raise ValueError("A managed secret must be nonempty and environment-safe")


def secret_environment(secrets: tuple[ProcessSecret, ...]) -> dict[str, str]:
    values = {item.name: item.value for item in secrets}
    if len(values) != len(secrets):
        raise ValueError("Duplicate managed secret name")
    return values
