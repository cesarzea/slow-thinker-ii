"""The platform catalog: available component declarations and LLM entries."""

from collections.abc import Iterable

from ._declaration import ComponentDeclaration
from ._llm import LlmEntry
from ._refs import OUTPUT, TRIGGER, ComponentRef

_PLATFORM = (TRIGGER, OUTPUT)


class Catalog:
    def __init__(
        self, components: Iterable[ComponentDeclaration], llms: Iterable[LlmEntry]
    ) -> None:
        self._components: dict[ComponentRef, ComponentDeclaration] = {}
        for declaration in components:
            if declaration.ref in self._components:
                raise ValueError(f"Duplicate component {declaration.ref}")
            self._components[declaration.ref] = declaration
        self._llms: dict[str, LlmEntry] = {}
        for entry in llms:
            if entry.id in self._llms:
                raise ValueError(f"Duplicate LLM entry {entry.id}")
            self._llms[entry.id] = entry

    def component(self, ref: ComponentRef) -> ComponentDeclaration | None:
        return self._components.get(ref)

    def components(self) -> tuple[ComponentDeclaration, ...]:
        """Platform components first, then the others by type and version."""
        return tuple(sorted(self._components.values(), key=_catalog_order))

    def llm(self, entry_id: str) -> LlmEntry | None:
        return self._llms.get(entry_id)

    def llms(self) -> tuple[LlmEntry, ...]:
        """Entries in configuration order."""
        return tuple(self._llms.values())


def _catalog_order(declaration: ComponentDeclaration) -> tuple[int, str, tuple[int, ...]]:
    ref = declaration.ref
    rank = _PLATFORM.index(ref) if ref in _PLATFORM else len(_PLATFORM)
    return rank, ref.type, tuple(int(part) for part in ref.version.split("."))
