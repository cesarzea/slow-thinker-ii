"""Public durable resource operations and standard component hosting boundary."""

from ._hosting import KeyValueMemoryHost
from ._memory import KeyValueMemory

__all__ = ["KeyValueMemory", "KeyValueMemoryHost"]
