"""Trusted preparation recipes; graphs cannot supply build or launch code."""

from dataclasses import dataclass

TARGETS = ("llm-call", "router", "memory")


@dataclass(frozen=True)
class PreparationTarget:
    """Source projects built into one closure, and the package that ships the component."""

    projects: tuple[str, ...]
    module: str


def target(name: str) -> PreparationTarget:
    """Each component is prepared with the host SDK it imports."""
    if name not in TARGETS:
        raise ValueError("Unknown component preparation target")
    module = "slow_thinker_" + name.replace("-", "_")
    return PreparationTarget(("components/host", f"components/{name}"), module)
