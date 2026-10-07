"""The configured installed components: their declarations and how to launch them."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from slow_thinker_ii.catalog import ComponentDeclaration, ComponentRef

from ._integrity import declared
from ._store import InstallationCatalog


@dataclass(frozen=True)
class InstalledComponent:
    resolution: str  # resolution identity
    declaration: ComponentDeclaration
    module: str  # entry module run with `python -m`


class InstalledComponents:
    """Every configured resolution, verified at construction; a `LaunchTarget` for the hosts.

    Each launch verifies the component's resolution again before naming its interpreter.
    """

    def __init__(self, catalog: InstallationCatalog, resolutions: Sequence[str]) -> None:
        self._catalog = catalog
        installed: list[InstalledComponent] = []
        for identity in resolutions:
            resolution = catalog.verify(identity)
            declaration = declared(resolution.inspection, resolution.registration)
            installed.append(
                InstalledComponent(identity, declaration, resolution.registration.module)
            )
        self._components = tuple(installed)
        self._by_ref = {item.declaration.ref: item for item in installed}
        if len(self._by_ref) != len(installed):
            raise ValueError("Two configured resolutions install the same component version")

    def components(self) -> tuple[InstalledComponent, ...]:
        return self._components

    def interpreter(self, ref: ComponentRef) -> Path:
        return self._catalog.interpreter(self._component(ref).resolution)

    def module(self, ref: ComponentRef) -> str:
        return self._component(ref).module

    def _component(self, ref: ComponentRef) -> InstalledComponent:
        component = self._by_ref.get(ref)
        if component is None:
            raise LookupError(f"No configured resolution installs {ref}")
        return component
