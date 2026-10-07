"""Secrets from the process environment: only named variables, whose values are never shown."""

import re
from collections.abc import Mapping

OPERATOR_TOKEN = "SLOW_THINKER_OPERATOR_TOKEN"
_TOKEN = re.compile(r"[!-~]{32,128}")  # visible ASCII, usable in an Authorization header


class EnvironmentSecrets:
    """Reads credentials from `environment`; errors name the variable, never its value."""

    def __init__(self, environment: Mapping[str, str]) -> None:
        self._environment = environment

    def require(self, name: str, purpose: str) -> str:
        value = self._environment.get(name, "")
        if not value:
            raise ValueError(f"The environment variable {name} ({purpose}) is not set.")
        return value

    def operator_token(self) -> str:
        token = self.require(OPERATOR_TOKEN, "the operator token")
        if _TOKEN.fullmatch(token) is None:
            raise ValueError(
                f"The environment variable {OPERATOR_TOKEN} must hold 32 to 128 visible ASCII "
                "characters without spaces."
            )
        return token
