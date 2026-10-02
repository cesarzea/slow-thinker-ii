"""Public side-effect-free schema inventory from trusted registered descriptors."""

from pathlib import Path

from slow_thinker_ii.contracts import JsonObject, decode_json, json_object

from ._validation._schemas import LocalSchemas
from ._validation._types import descriptors


class ComponentCatalog:
    def __init__(self, schemas: Path, directory: Path, registered: tuple[str, ...] = ()) -> None:
        self._schemas = LocalSchemas(schemas)
        self._types = descriptors(directory, self._schemas, registered)
        self._documents = tuple(path.read_text() for path in sorted(schemas.glob("*.schema.json")))

    def components(self) -> tuple[JsonObject, ...]:
        return tuple(json_object(value) for _, value in sorted(self._types.items()))

    def graph_schema(self) -> JsonObject:
        return json_object(self._schemas.graph)

    def schema_documents(self) -> JsonObject:
        result: JsonObject = {}
        for source in self._documents:
            value = json_object(decode_json(source))
            result[str(value["$id"])] = value
        return result
