"""Fresh invocation objects backed by externally owned transactional memory."""

import asyncio
import sqlite3
from pathlib import Path

from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, JsonObject, Operation, ToolReply, validate_value

from ._memory import KeyValueMemory
from ._schemas import CONFIG_SCHEMA, operations
from ._validation import bounded_integer, key


class KeyValueMemoryHost:
    def __init__(
        self,
        config: JsonObject,
        declared: tuple[Operation, ...],
        path: Path,
        namespace: str,
    ) -> None:
        self._operations = self.describe(config)
        if declared != self._operations:
            raise ValueError("Configured memory operation schemas do not match")
        self._path, self._namespace = path, namespace
        self._entries = bounded_integer(config.get("max_entries", 1000), 10000)
        self._bytes = bounded_integer(config.get("max_value_bytes", 65536), 65536)

    @classmethod
    def describe(cls, config: JsonObject) -> tuple[Operation, ...]:
        validate_value(config, CONFIG_SCHEMA)
        key(config["namespace"])
        bounded_integer(config.get("max_entries", 1000), 10000)
        bounded_integer(config.get("max_value_bytes", 65536), 65536)
        return operations()

    def operations(self) -> tuple[Operation, ...]:
        return self._operations

    async def invoke(self, name: str, arguments: JsonObject, context: Invocation) -> ToolReply:
        del context
        try:
            operation = next((item for item in self._operations if item.name == name), None)
            if operation is None:
                raise ValueError("Unsupported memory operation")
            validate_value(arguments, operation.input_schema)
            memory = KeyValueMemory(
                self._path, self._namespace, max_entries=self._entries, max_value_bytes=self._bytes
            )
            methods = {
                "get": memory.get,
                "put": memory.put,
                "delete": memory.delete,
                "list": memory.list,
            }
            return ToolReply(await asyncio.to_thread(methods[name], arguments))
        except (ValueError, sqlite3.Error, OSError) as error:
            reason = str(error) if isinstance(error, ValueError) else "Memory storage unavailable"
            raise MCPError(code=-32603, message="memory_failed", data={"reason": reason}) from error
