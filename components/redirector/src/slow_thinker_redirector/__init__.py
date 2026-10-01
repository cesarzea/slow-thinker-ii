"""Public deterministic selector component and optional independent MCP host."""

from ._config import parse_config
from ._hosting import RedirectorHost
from ._redirector import Redirector
from ._types import RedirectorConfig

__all__ = ["Redirector", "RedirectorConfig", "RedirectorHost", "parse_config"]
