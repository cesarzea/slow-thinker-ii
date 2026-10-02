"""Personal experiment selection and authoring use cases."""

from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import GraphSummary

from ._cursors import LibraryCursors, Position
from ._ports import BundledSource, DefinitionRepository, DefinitionValidator
from ._records import (
    DefinitionError,
    GraphReference,
    LibraryItem,
    LibraryPage,
    SaveResult,
    ValidatedDefinition,
)


class ExperimentLibrary:
    def __init__(
        self,
        bundled: BundledSource,
        repository: DefinitionRepository,
        validator: DefinitionValidator,
        cursor_key: bytes,
    ) -> None:
        self._bundled, self._repository, self._validator = bundled, repository, validator
        self._cursors = LibraryCursors(cursor_key)

    def definition(self, graph_id: str, revision: str) -> str:
        reference = GraphReference(graph_id, revision)
        if self._is_bundled(reference):
            return self._bundled.definition(graph_id, revision)
        source = self._repository.read(reference)
        if source is None:
            raise DefinitionError("definition_not_found")
        return source

    def detail(self, graph_id: str, revision: str) -> str:
        return self._validator.detail(self.definition(graph_id, revision))

    def draft(self, source: GraphReference, target: GraphReference) -> str:
        """Return an unsaved canonical variant, preserving all non-identity values."""
        if source == target:
            raise DefinitionError("invalid_definition")
        value = json_object(decode_json(self.definition(source.graph_id, source.revision)))
        value["graph_id"], value["revision"] = target.graph_id, target.revision
        value["derived_from"] = {"graph_id": source.graph_id, "revision": source.revision}
        return self.validate(encode_json(value)).definition_json

    def validate(self, source: str) -> ValidatedDefinition:
        document = self._validator.validate(source)
        self._parent(document)
        return document

    def save(self, source: str) -> SaveResult:
        document = self._validator.validate(source)
        parent_is_bundled = self._parent(document, check_personal=False)
        reference = document.reference
        if self._is_bundled(reference):
            original = self._bundled.definition(reference.graph_id, reference.revision)
            if encode_json(decode_json(original)) != document.definition_json:
                raise DefinitionError("definition_conflict")
            return SaveResult(reference, False)
        return SaveResult(reference, self._repository.insert(document, parent_is_bundled))

    def page(self, limit: int = 50, cursor: str | None = None) -> LibraryPage:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise DefinitionError("invalid_query")
        bundles = self._bundled.summaries()
        start = Position() if cursor is None else self._cursors.decode(cursor, limit, len(bundles))
        selected = bundles[start.bundle : start.bundle + limit]
        items = [self._bundled_item(summary) for summary in selected]
        stored = self._repository.page(start.after, start.through, limit - len(items))
        items.extend(self._personal_item(source) for source in stored.definitions)
        next_position = Position(start.bundle + len(selected), stored.last, stored.through)
        has_more = next_position.bundle < len(bundles) or stored.has_more
        token = self._cursors.encode(next_position, limit) if has_more else None
        return LibraryPage(tuple(items), token)

    def _is_bundled(self, reference: GraphReference) -> bool:
        return any(
            (item.graph_id, item.revision) == (reference.graph_id, reference.revision)
            for item in self._bundled.summaries()
        )

    def _parent(self, document: ValidatedDefinition, check_personal: bool = True) -> bool:
        parent = document.parent
        if parent is None:
            return False
        if parent == document.reference:
            raise DefinitionError("invalid_definition")
        bundled = self._is_bundled(parent)
        if check_personal and not bundled and self._repository.read(parent) is None:
            raise DefinitionError("definition_parent_missing")
        return bundled

    def _bundled_item(self, summary: GraphSummary) -> LibraryItem:
        source = self._bundled.definition(summary.graph_id, summary.revision)
        document = self._validator.validate(source)
        return LibraryItem(summary, "bundled", document.parent)

    def _personal_item(self, source: str) -> LibraryItem:
        document = self._validator.validate(source)
        return LibraryItem(document.summary, "personal", document.parent)
