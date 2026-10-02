"""Definition HTTP fixtures have isolated persistent libraries and operator authority."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from support.definition_http import DefinitionHttp, definition_http


@pytest.fixture
async def definitions(tmp_path: Path) -> AsyncIterator[DefinitionHttp]:
    case = definition_http(tmp_path)
    try:
        yield case
    finally:
        await case.client.aclose()
