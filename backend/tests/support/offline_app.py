"""Browser-test composition with isolated storage and a public catalogue fixture."""

from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI
from slow_thinker_ii.bootstrap import create_app as application

from .browser_execution import BrowserExecution
from .catalog import RecordedCatalog
from .workspace_tariffs import RecordedDeepSeek

WORKSPACE = TemporaryDirectory(prefix="slow-thinker-ii-browser-")


def create_app() -> FastAPI:
    return application(
        Path(WORKSPACE.name) / "test.sqlite3",
        RecordedCatalog(),
        BrowserExecution(),
        {"deepseek.flash.direct.v1": RecordedDeepSeek()},
    )
