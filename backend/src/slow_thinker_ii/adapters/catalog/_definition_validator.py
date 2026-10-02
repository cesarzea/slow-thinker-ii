"""Static validation and projections for canonical editable graph definitions."""

from pathlib import Path

from referencing.exceptions import Unresolvable

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import graph_detail

from ._validation import LocalSchemas, validate_definition


class GraphDefinitionValidator:
    def __init__(self, schema_directory: Path, descriptor_directory: Path) -> None:
        self._schemas, self._descriptors = schema_directory, descriptor_directory

    def validate(self, source: str) -> library.ValidatedDefinition:
        document, _ = self._validated(source)
        return document

    def detail(self, source: str) -> str:
        document, roles = self._validated(source)
        return encode_json(graph_detail(json_object(decode_json(document.definition_json)), roles))

    def _validated(
        self, source: str
    ) -> tuple[library.ValidatedDefinition, dict[str, tuple[str, ...]]]:
        try:
            source.encode("utf-8", errors="strict")
            decoded = decode_json(source)
            encode_json(decoded).encode("utf-8", errors="strict")
        except (ValueError, UnicodeError, RecursionError) as error:
            raise library.DefinitionError("invalid_json") from error
        try:
            value = json_object(decoded)
            return validate_definition(value, LocalSchemas(self._schemas), self._descriptors)
        except library.DefinitionError:
            raise
        except (ValueError, KeyError, Unresolvable, RecursionError) as error:
            issue = library.DefinitionIssue(
                "", "Definition does not satisfy the supported graph contract."
            )
            raise library.DefinitionError("invalid_definition", (issue,)) from error
