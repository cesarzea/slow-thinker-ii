"""LLM Call component: one model call per activation through the platform's LLM service."""

from ._component import LLMCall
from ._config import LLMCallConfig, parse_config
from ._main import main
from ._model import Message

__all__ = ["LLMCall", "LLMCallConfig", "Message", "main", "parse_config"]
