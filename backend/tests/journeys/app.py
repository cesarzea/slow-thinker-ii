"""Browser-journey backend: development component hosts and a scripted simulated provider."""

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI
from slow_thinker_ii.adapters.providers import SimulatedProvider
from slow_thinker_ii.bootstrap import AppOverrides, load_configuration
from slow_thinker_ii.bootstrap import create_app as application
from slow_thinker_ii.catalog import ComponentRef, parse_declaration

from .configuration import journey_configuration
from .declarations import development_declarations

WORKSPACE = TemporaryDirectory(prefix="slow-thinker-ii-journeys-")
MODULES = {
    "llm-call": "slow_thinker_llm_call",
    "router": "slow_thinker_router",
    "memory": "slow_thinker_memory",
}
REVIEW_SCORES = ('{"score": 5}', '{"score": 8}')


class DevelopmentHosts:
    """Launch component hosts from the development environment's editable packages."""

    def interpreter(self, ref: ComponentRef) -> Path:
        return Path(sys.executable)

    def module(self, ref: ComponentRef) -> str:
        return MODULES[ref.type]


def create_app() -> FastAPI:
    root = Path(WORKSPACE.name)
    document = journey_configuration(root, os.environ)
    path = root / "configuration.json"
    path.write_text(json.dumps(document))
    overrides = AppOverrides(
        components=tuple(parse_declaration(item) for item in development_declarations()),
        launch_targets=DevelopmentHosts(),
        provider=SimulatedProvider({"deepseek/deepseek-flash": REVIEW_SCORES}),
    )
    return application(load_configuration(path), os.environ, overrides)
