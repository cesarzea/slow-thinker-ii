"""Each component's interpreter and module, looked up once per launch, off the event loop."""

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from slow_thinker_ii.catalog import ComponentRef

from ._readiness import NotReady
from ._settings import LaunchTarget


@dataclass(frozen=True)
class Target:
    interpreter: Path
    module: str


async def resolve(
    targets: LaunchTarget, refs: Iterable[ComponentRef]
) -> dict[ComponentRef, Target | NotReady]:
    """One lookup per distinct component, all in worker threads at once: a launch target
    may verify an installation, running a subprocess and hashing files, for a second or more."""
    distinct = list(dict.fromkeys(refs))
    found = await asyncio.gather(*(asyncio.to_thread(_lookup, targets, ref) for ref in distinct))
    return dict(zip(distinct, found, strict=True))


def _lookup(targets: LaunchTarget, ref: ComponentRef) -> Target | NotReady:
    try:
        return Target(targets.interpreter(ref), targets.module(ref))
    except Exception as error:
        return NotReady("launch_failed", f"it is not installed: {error}")
