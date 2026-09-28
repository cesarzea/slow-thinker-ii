"""Resolve only named environment credentials registered by trusted backend composition."""

import os
import re
from collections.abc import Mapping
from typing import Protocol

from slow_thinker_ii.application import PreparationRejected


class SecretSource(Protocol):
    def resolve(self, reference: str) -> str: ...


class EnvironmentSecrets:
    def __init__(self, references: Mapping[str, str]) -> None:
        if any(
            not key or not re.fullmatch(r"[A-Z_][A-Z0-9_]*", value)
            for key, value in references.items()
        ):
            raise ValueError("Credential references need explicit environment variable names")
        self._references = dict(references)

    def resolve(self, reference: str) -> str:
        name = self._references.get(reference)
        value = None if name is None else os.environ.get(name)
        if not value:
            raise PreparationRejected("credential_unavailable")
        return value
